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

function renderBulletList(card, title, bullets) {
  if (!bullets.length) return;
  card.appendChild(el("h4", "summary-subhead", title));
  const list = el("ul", "evidence-list");
  for (const bullet of bullets) {
    const item = el("li", null, bullet.text);
    if (bullet.chunk_ids && bullet.chunk_ids.length) {
      item.appendChild(el("span", "evidence-page",
        `chunks ${bullet.chunk_ids.join(", ")}`));
    }
    list.appendChild(item);
  }
  card.appendChild(list);
}

function renderArtifact(artifact) {
  const card = el("article", "artifact");
  const head = el("div", "artifact-head");
  head.appendChild(el("h3", null, artifact.name));
  head.appendChild(el("div", "artifact-meta",
    `${fmt(artifact.supporting_chunk_ids.length)} cited chunks · ${artifact.source_documents.length} source document${artifact.source_documents.length === 1 ? "" : "s"}`));
  card.appendChild(head);

  if (!artifact.summarized) {
    card.appendChild(el("p", "artifact-grounding",
      "No generated summary yet — this artifact appears in the complete corpus download."));
    return card;
  }

  const body = el("div", "summary-body");
  body.appendChild(el("p", "summary-overview", artifact.overview));
  renderBulletList(body, "Contributions", artifact.contributions);
  renderBulletList(body, "Capabilities demonstrated", artifact.capabilities);
  if (artifact.why_it_mattered) {
    body.appendChild(el("h4", "summary-subhead", "Why it mattered"));
    body.appendChild(el("p", "summary-overview", artifact.why_it_mattered));
  }
  card.appendChild(body);

  if (artifact.source_documents.length) {
    const trace = el("div", "trace");
    trace.appendChild(document.createTextNode(
      artifact.source_documents.map((d) => d.split("/").pop()).join("  ·  ")));
    card.appendChild(trace);
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
      total += artifact.supporting_chunk_ids.length;
      sec.appendChild(renderArtifact(artifact));
    }
    profileBody.appendChild(sec);
  }

  if (profile.models && profile.models.length) {
    profileBody.appendChild(el("p", "resolved-note",
      `Summaries generated locally by ${profile.models.join(", ")}; assembly and citations are deterministic.`));
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
