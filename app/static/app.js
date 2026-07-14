/* CareerPilot profile renderer — fetches the deterministic profile and
   builds the evidence ledger. No templating library; the DOM is the
   template. */

const renderBtn = document.getElementById("render-btn");
const profileBody = document.getElementById("profile-body");
const emptyState = document.getElementById("empty-state");

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

const fmt = (n) => n.toLocaleString("en-US");

function setPipeline(p) {
  document.getElementById("stat-documents").textContent = fmt(p.documents);
  document.getElementById("stat-chunks").textContent = fmt(p.chunks);
  document.getElementById("stat-canonical").textContent = fmt(p.canonical_chunks);
  document.getElementById("stat-artifacts").textContent = fmt(p.artifacts);
}

function renderArtifact(artifact) {
  const card = el("article", "artifact");
  const head = el("div", "artifact-head");
  head.appendChild(el("h3", null, artifact.name));
  head.appendChild(el("div", "artifact-meta",
    `${fmt(artifact.evidence_count)} evidence lines · ${artifact.source_count} source document${artifact.source_count === 1 ? "" : "s"}`));
  card.appendChild(head);
  card.appendChild(el("p", "artifact-grounding", artifact.grounded_in));

  if (artifact.sources.length) {
    const details = el("details");
    details.appendChild(el("summary", null,
      `evidence ledger — ${fmt(artifact.evidence_count)} lines`));
    for (const group of artifact.sources) {
      const wrap = el("div", "source-group");
      const trace = el("div", "trace");
      const origin = group.source_file || group.document;
      trace.appendChild(document.createTextNode(origin));
      if (group.source_sha256) {
        trace.appendChild(el("span", "sha", `  ·  sha256 ${group.source_sha256.slice(0, 12)}…`));
      }
      wrap.appendChild(trace);
      const list = el("ul", "evidence-list");
      for (const line of group.lines) {
        const item = el("li", null, line.text);
        if (line.page) item.appendChild(el("span", "evidence-page", `p.${line.page}`));
        list.appendChild(item);
      }
      wrap.appendChild(list);
      details.appendChild(wrap);
    }
    card.appendChild(details);
  }
  return card;
}

function renderProfile(profile) {
  setPipeline(profile.pipeline);
  emptyState.remove();
  profileBody.textContent = "";

  let total = 0;
  let delay = 0;
  for (const section of profile.sections) {
    if (!section.artifacts.length) continue;
    const sec = el("section", "profile-section reveal");
    sec.style.animationDelay = `${delay}ms`;
    delay += 90;
    const head = el("div", "section-head");
    head.appendChild(el("h2", null, section.title));
    head.appendChild(el("span", "section-count",
      `${section.artifacts.length} artifact${section.artifacts.length === 1 ? "" : "s"}`));
    sec.appendChild(head);
    for (const artifact of section.artifacts) {
      total += artifact.evidence_count;
      sec.appendChild(renderArtifact(artifact));
    }
    profileBody.appendChild(sec);
  }

  if (profile.resolved_references.length) {
    const notes = profile.resolved_references
      .map((r) => `“${r.name}” resolves to ${r.canonical}`)
      .join(" · ");
    profileBody.appendChild(el("p", "resolved-note", `Reference notes: ${notes}`));
  }

  document.getElementById("verify-count").textContent = fmt(total);
  document.getElementById("verify-line").hidden = false;
  renderBtn.textContent = "Re-render profile";
}

async function render() {
  renderBtn.disabled = true;
  renderBtn.textContent = "Rendering…";
  try {
    const response = await fetch("/api/profile");
    if (!response.ok) throw new Error(`profile endpoint returned ${response.status}`);
    renderProfile(await response.json());
  } catch (err) {
    profileBody.textContent = "";
    const fail = el("div", "empty-state");
    fail.appendChild(el("p", "empty-mark", "!"));
    fail.appendChild(el("p", null, "The profile could not be rendered."));
    fail.appendChild(el("p", "empty-hint",
      `${err.message}. Check that the database is running, then render again.`));
    profileBody.appendChild(fail);
    renderBtn.textContent = "Render profile";
  } finally {
    renderBtn.disabled = false;
  }
}

renderBtn.addEventListener("click", render);
