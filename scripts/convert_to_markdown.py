"""Convert .pdf and .docx career-evidence files to Markdown.

Implementation step 2 (and reusable for step 3) of claude.md: deterministic,
auditable, no LLM involved. Every output file carries YAML frontmatter that
traces it back to the exact source document (relative path + SHA-256), so any
downstream chunk can be verified against the original bytes.

Default run converts `2nd brain/career artifacts/raw drive` into
`2nd brain/career artifacts/converted drive`:

    python scripts/convert_to_markdown.py

Any other folder pair can be converted with --input/--output:

    python scripts/convert_to_markdown.py --input "2nd brain/career artifacts/raw education" ^
                                          --output "2nd brain/career artifacts/raw education"

Re-running on unchanged sources produces byte-identical output (no timestamps,
sorted file order, normalized newlines). A `_manifest.json` in the output
folder records the full source -> output mapping with hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from importlib.metadata import version
from pathlib import Path

import mammoth
import pdfplumber

MAMMOTH_VERSION = version("mammoth")
PDFPLUMBER_VERSION = version("pdfplumber")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "2nd brain" / "career artifacts" / "raw drive"
DEFAULT_OUTPUT = REPO_ROOT / "2nd brain" / "career artifacts" / "converted drive"

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _discard_image(image) -> dict:
    # Embedded images can't carry text evidence; dropping them keeps the
    # Markdown small and the conversion deterministic.
    return {"src": ""}


def convert_docx(path: Path) -> tuple[str, list[str]]:
    with path.open("rb") as f:
        result = mammoth.convert_to_markdown(
            f, convert_image=mammoth.images.img_element(_discard_image)
        )
    warnings = [m.message for m in result.messages]
    return result.value, warnings


def convert_pdf(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                text = "*[no extractable text on this page]*"
                warnings.append(f"page {number}: no extractable text")
            pages.append(f"<!-- source page {number} -->\n\n{text.strip()}")
    return "\n\n".join(pages), warnings


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def yaml_escape(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def frontmatter(source: Path, source_hash: str, converter: str, warnings: list[str]) -> str:
    relative = source.resolve().relative_to(REPO_ROOT).as_posix()
    lines = [
        "---",
        f"source_file: {yaml_escape(relative)}",
        f"source_sha256: {source_hash}",
        f"converter: {converter}",
    ]
    if warnings:
        lines.append("conversion_warnings:")
        lines.extend(f"  - {yaml_escape(w)}" for w in warnings)
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def output_name(source: Path, taken: set[str]) -> str:
    # Keep the human-readable stem; suffix with the source extension only on
    # collision (e.g. report.pdf and report.docx in the same folder).
    candidate = source.stem + ".md"
    if candidate.lower() in taken:
        candidate = f"{source.stem}.{source.suffix.lstrip('.')}.md"
    taken.add(candidate.lower())
    return candidate


def convert_folder(input_dir: Path, output_dir: Path) -> int:
    if not input_dir.is_dir():
        print(f"error: input folder not found: {input_dir}", file=sys.stderr)
        return 1

    sources = sorted(
        (p for p in input_dir.iterdir()
         if p.suffix.lower() in SUPPORTED_EXTENSIONS and not p.name.startswith("~$")),
        key=lambda p: p.name.lower(),
    )
    if not sources:
        print(f"no .pdf or .docx files found in {input_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    taken: set[str] = set()
    failures = 0

    for source in sources:
        name = output_name(source, taken)
        destination = output_dir / name
        try:
            if source.suffix.lower() == ".docx":
                body, warnings = convert_docx(source)
                converter = f"mammoth {MAMMOTH_VERSION}"
            else:
                body, warnings = convert_pdf(source)
                converter = f"pdfplumber {PDFPLUMBER_VERSION}"
        except Exception as exc:  # noqa: BLE001 - one bad file must not stop the batch
            failures += 1
            print(f"FAIL  {source.name}: {exc}", file=sys.stderr)
            continue

        source_hash = sha256_of(source)
        markdown = frontmatter(source, source_hash, converter, warnings) + normalize(body)
        destination.write_text(markdown, encoding="utf-8", newline="\n")

        manifest.append({
            "source_file": source.resolve().relative_to(REPO_ROOT).as_posix(),
            "source_sha256": source_hash,
            "output_file": destination.resolve().relative_to(REPO_ROOT).as_posix(),
            "converter": converter,
            "warnings": warnings,
        })
        note = f" ({len(warnings)} warning{'s' if len(warnings) != 1 else ''})" if warnings else ""
        print(f"ok    {source.name} -> {name}{note}")

    manifest_path = output_dir / "_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"\nconverted {len(manifest)}/{len(sources)} files -> {output_dir}")
    print(f"manifest: {manifest_path}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="folder containing .pdf/.docx files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="folder to write .md files into")
    args = parser.parse_args()
    return convert_folder(args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
