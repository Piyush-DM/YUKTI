/*
 * YUKTI Investment Committee Workspace.
 *
 * One screen, four views over a case: Overview, Material, Judgment, Audit.
 * The server owns every fact; this file renders what it is given and posts what
 * the user typed. It computes no judgment of its own — if a number is on the
 * screen, the record contains it.
 *
 * Plain DOM, no framework, no build step, matching the convention already set
 * by the website and the existing prototype UI.
 */

const state = {
  schedule: null,
  reference: null,
  cases: [],
  selectedId: null,
  detail: null,
  // Which judgment is on screen. null means the one in force; an id means the
  // reader has opened a superseded judgment to audit a decision made against it.
  judgmentId: null,
  tab: "overview",
  message: null,
  busy: false,
  // The staged read-out of one analysis run. null except during and just after
  // a run; cleared whenever the reader moves somewhere else.
  execution: null,
};

const registerList = document.querySelector("#register-list");
const stage = document.querySelector("#stage");
const topbarMeta = document.querySelector("#topbar-meta");

document.querySelector("#open-case-button").addEventListener("click", () => {
  state.selectedId = null;
  state.detail = null;
  state.message = null;
  state.tab = "intake";
  render();
});

boot();

async function boot() {
  try {
    state.schedule = await api("GET", "/api/schedule");
    state.reference = await api("GET", "/api/reference-material");
    await refreshCases();
  } catch (error) {
    state.message = { kind: "error", text: describe(error) };
  }
  render();
}

async function api(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "The workspace could not complete that.");
  }
  return payload;
}

function describe(error) {
  return error && error.message ? error.message : String(error);
}

async function refreshCases() {
  const payload = await api("GET", "/api/cases");
  state.cases = payload.cases;
}

async function selectCase(caseId) {
  state.busy = true;
  render();
  try {
    state.detail = await api("GET", `/api/cases/${caseId}`);
    state.selectedId = caseId;
    state.judgmentId = null;
    state.message = null;
    state.execution = null;
    if (state.tab === "intake") {
      state.tab = "overview";
    }
  } catch (error) {
    state.message = { kind: "error", text: describe(error) };
  }
  state.busy = false;
  render();
}

async function act(fn) {
  state.busy = true;
  state.message = null;
  render();
  try {
    await fn();
  } catch (error) {
    state.message = { kind: "error", text: describe(error) };
  }
  state.busy = false;
  render();
}

/* ---------------------------------------------------------------- render */

function render() {
  renderTopbar();
  renderRegister();
  renderStage();
}

function renderTopbar() {
  const decided = state.cases.filter((item) => item.status === "Decided").length;
  topbarMeta.textContent = state.cases.length
    ? `${state.cases.length} case${state.cases.length === 1 ? "" : "s"} · ${decided} decided`
    : "";
}

function renderRegister() {
  registerList.replaceChildren();
  if (!state.cases.length) {
    registerList.append(
      el(
        "div",
        { class: "register-empty" },
        el("p", { class: "register-empty-lead" }, "No cases yet"),
        el(
          "p",
          {},
          "A case is one decision the committee has to make. Open one to " +
            "start assembling material against the diligence schedule.",
        ),
      ),
    );
    return;
  }
  state.cases.forEach((item) => {
    const card = el("button", {
      class: "register-card",
      type: "button",
      "aria-current": String(item.case_id === state.selectedId),
    });
    // Status is split from owner so the register can be scanned by state
    // without reading each line. Same two values as before, same order.
    card.append(
      el("span", { class: "name" }, item.title),
      el(
        "span",
        { class: "meta" },
        el(
          "span",
          { class: `case-status is-${item.status.toLowerCase().replace(/\s+/g, "-")}` },
          item.status,
        ),
        el("span", { class: "case-owner" }, item.owner),
      ),
    );
    card.addEventListener("click", () => selectCase(item.case_id));
    registerList.append(card);
  });
}

function renderStage() {
  stage.replaceChildren();
  const inner = el("div", { class: "stage-inner" });
  stage.append(inner);

  if (state.message) {
    inner.append(
      el(
        "div",
        { class: `message ${state.message.kind === "error" ? "is-error" : ""}` },
        state.message.text,
      ),
    );
  }

  if (state.tab === "intake") {
    inner.append(renderIntake());
    return;
  }

  if (!state.detail) {
    inner.append(renderEmptyState());
    return;
  }

  inner.append(renderCaseHead(), renderTabs());
  const views = {
    overview: renderOverview,
    material: renderMaterial,
    judgment: renderJudgment,
    audit: renderAudit,
  };
  inner.append((views[state.tab] || renderOverview)());
}

function renderEmptyState() {
  const box = el("div", { class: "empty-state" });
  box.append(
    el("h2", {}, "No case selected"),
    el(
      "p",
      {},
      "A case is one decision the committee has to make. Select a case from " +
        "the register, or open a new one to start assembling material against " +
        "the diligence schedule.",
    ),
  );
  return box;
}

/* ---------------------------------------------------------------- intake */

function renderIntake() {
  const panel = el("section", { class: "panel" });
  panel.append(el("h3", {}, "Open a case"));
  panel.append(
    el(
      "p",
      { class: "panel-note" },
      "Record what the committee is being asked to decide. Material and " +
        "analysis come next.",
    ),
  );

  const form = el("form", { class: "form-grid" });
  form.append(
    field("Company", "company", ""),
    field("Stage", "stage", ""),
    field("Sector", "sector", ""),
    field("Case owner", "owner", ""),
    field("Requested decision", "requested_decision", "", true),
    textField("Thesis", "thesis", "", 4),
  );

  const actions = el("div", { class: "actions wide" });
  const submit = el("button", { class: "primary", type: "submit" }, "Open case");
  submit.disabled = state.busy;
  actions.append(submit);
  form.append(actions);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    act(async () => {
      const detail = await api("POST", "/api/cases", {
        company: data.get("company"),
        stage: data.get("stage"),
        sector: data.get("sector"),
        owner: data.get("owner"),
        requested_decision: data.get("requested_decision"),
        thesis: data.get("thesis"),
      });
      await refreshCases();
      state.detail = detail;
      state.selectedId = detail.case.case_id;
      state.tab = "material";
    });
  });

  panel.append(form);
  return panel;
}

/* ------------------------------------------------------------ case shell */

function renderCaseHead() {
  const record = state.detail.case;
  const head = el("header", { class: "case-head" });
  head.append(el("h1", {}, state.detail.title));
  head.append(el("p", { class: "decision-ask" }, record.requested_decision));

  const facts = el("div", { class: "case-facts" });
  facts.append(
    el("span", { class: `status-chip ${state.detail.status === "Decided" ? "is-decided" : ""}` },
      state.detail.status),
    el("span", {}, record.sector),
    el("span", {}, `Owner: ${record.owner}`),
    el("span", {}, `Opened ${record.opened_on}`),
  );
  head.append(facts);
  return head;
}

function renderTabs() {
  const nav = el("nav", { class: "tabs" });
  const tabs = [
    ["overview", "Overview"],
    ["material", "Material"],
    ["judgment", "Judgment"],
    ["audit", "Audit"],
  ];
  tabs.forEach(([key, label]) => {
    const button = el("button", {
      class: "tab",
      type: "button",
      "aria-selected": String(state.tab === key),
    }, label);
    button.addEventListener("click", () => {
      state.tab = key;
      // Leaving the judgment view ends the read-out; coming back shows the
      // settled judgment rather than replaying an execution that is over.
      state.execution = null;
      render();
    });
    nav.append(button);
  });
  return nav;
}

/* -------------------------------------------------------------- overview */

function renderOverview() {
  const wrap = el("div", {});
  const record = state.detail.case;
  const total = state.schedule.schedule.length;
  const recorded = total - state.detail.outstanding.length;

  const coverage = el("section", { class: "panel" });
  coverage.append(el("h3", {}, "Diligence completeness"));
  coverage.append(
    el("p", { class: "numeric" }, `${recorded} of ${total} scheduled figures recorded`),
  );
  const bar = el("div", { class: "coverage-bar" });
  bar.append(el("span", { style: `width: ${(recorded / total) * 100}%` }));
  coverage.append(bar);
  if (state.detail.outstanding.length) {
    coverage.append(
      el("p", { class: "panel-note" }, "Still outstanding:"),
      list(state.detail.outstanding.map((entry) => `${entry.label} — ${entry.guidance}`)),
    );
  } else {
    coverage.append(el("p", { class: "panel-note" }, "The schedule is complete."));
  }
  wrap.append(coverage);

  const thesis = el("section", { class: "panel" });
  thesis.append(el("h3", {}, "Thesis"));
  thesis.append(el("p", {}, record.thesis || "No thesis recorded."));
  wrap.append(thesis);

  const snapshots = state.detail.case.snapshots || [];
  if (snapshots.length) {
    const panel = el("section", { class: "panel" });
    panel.append(el("h3", {}, `Material register (${snapshots.length})`));
    panel.append(
      el(
        "p",
        { class: "panel-note" },
        "Every state this case's material has held, oldest first. A judgment is " +
          "formed from exactly one of these, and says which.",
      ),
    );
    snapshots.forEach((snapshot) => {
      const row = el("div", { class: "position-row" });
      row.append(
        el("span", { class: "who" }, `${snapshot.snapshot_id} (v${snapshot.version})`),
        el("span", { class: "numeric" }, snapshot.recorded_on),
        el("span", { class: "digest" }, `${snapshot.material_digest.slice(0, 16)}…`),
      );
      panel.append(row);
    });
    wrap.append(panel);
  }

  wrap.append(renderLedger());
  return wrap;
}

function renderLedger() {
  const panel = el("section", { class: "panel" });
  panel.append(el("h3", {}, "Decision ledger"));
  const entries = state.detail.case.ledger;
  if (!entries.length) {
    panel.append(
      el("p", { class: "panel-note" },
        "No decision recorded. The ledger holds what the committee chose, " +
        "which is kept separate from what the analysis recommended."),
    );
    return panel;
  }
  const verification = new Map(
    (state.detail.ledger_verification || []).map((check) => [check.entry_id, check]),
  );

  entries.forEach((entry) => {
    const block = el("div", { class: "finding" });
    block.append(
      el("p", {}, el("strong", {}, entry.decision), ` — ${entry.decided_by}, ${entry.recorded_on}`),
      el("p", { class: "panel-note" }, entry.rationale),
      el("p", { class: "cites" },
        `Against judgment: ${entry.judgment_recommendation} at ${entry.judgment_confidence} confidence`),
    );

    // A decision is only worth having if it still resolves to the judgment it
    // was taken against. That is checked, not assumed, and shown either way.
    const check = verification.get(entry.entry_id);
    const line = el("p", { class: "cites" });
    const open = el("button", { class: "link", type: "button" }, entry.judgment_id);
    open.addEventListener("click", () => {
      state.tab = "judgment";
      viewJudgment(entry.judgment_id);
    });
    line.append("Bound to ", open, " · ");
    // Reasoning identity and material identity are separate claims, so they are
    // reported separately. A decision can verify against its record while its
    // material is unidentified, and reading that as fully verified would be the
    // exact overstatement this layer exists to prevent.
    if (!check) {
      line.append(el("span", { class: "unverified" }, "NOT VERIFIED"));
    } else {
      line.append(
        check.record_resolves
          ? el("span", { class: "verified" }, "reasoning verified")
          : el("span", { class: "unverified" }, "RECORD DOES NOT RESOLVE"),
        " · ",
        check.material_resolves
          ? el("span", { class: "verified" }, "material verified")
          : el(
              "span",
              { class: "unverified" },
              check.cited_material ? "MATERIAL DOES NOT RESOLVE" : "MATERIAL NOT IDENTIFIED",
            ),
      );
    }
    block.append(line);
    panel.append(block);
  });
  return panel;
}

/* -------------------------------------------------------------- material */

function renderMaterial() {
  const wrap = el("form", { id: "material-form" });
  const record = state.detail.case;

  const sources = el("section", { class: "panel" });
  sources.append(el("h3", {}, "Source register"));
  sources.append(
    el("p", { class: "panel-note" },
      "Every figure must cite a source in this register. How a source came to " +
      "exist sets the ceiling on how confident any conclusion resting on it " +
      "can be."),
  );
  const table = el("table");
  table.append(
    el("thead", {}, row("th", ["Reference", "Description", "Standing", ""])),
  );
  const body = el("tbody", { id: "source-rows" });
  const existing = record.sources.length ? record.sources : [];
  existing.forEach((source) => body.append(sourceRow(source)));
  table.append(body);
  sources.append(table);

  const addSource = el("button", { type: "button" }, "Add source");
  addSource.addEventListener("click", () => {
    body.append(sourceRow({ label: "", origin: "", kind: "management" }));
  });
  const rowActions = el("div", { class: "row-actions" });
  rowActions.append(addSource);
  if (state.reference) {
    const useReference = el("button", { type: "button" }, "Use reference material");
    useReference.addEventListener("click", () => applyReference());
    rowActions.append(useReference);
  }
  sources.append(rowActions);
  wrap.append(sources);

  const figures = el("section", { class: "panel" });
  figures.append(el("h3", {}, "Diligence schedule"));
  figures.append(
    el("p", { class: "panel-note" },
      "Leave a figure blank if the material does not establish it. A blank is " +
      "recorded as a gap and reported; it is never treated as a zero or a no."),
  );
  const recorded = new Map(record.figures.map((figure) => [figure.metric, figure]));
  state.schedule.review_areas.forEach((area) => {
    const items = state.schedule.schedule.filter((entry) => entry.review_area === area);
    if (!items.length) return;
    const block = el("section", { class: "area-block" });
    block.append(el("h4", {}, area));
    const areaTable = el("table");
    areaTable.append(
      el("thead", {}, row("th", ["Figure", "Value", "Standing", "Sources"])),
    );
    const areaBody = el("tbody");
    items.forEach((entry) => areaBody.append(figureRow(entry, recorded.get(entry.metric))));
    areaTable.append(areaBody);
    block.append(areaTable);
    figures.append(block);
  });
  wrap.append(figures);

  const notes = el("section", { class: "panel" });
  notes.append(el("h3", {}, "Assumptions and flagged conflicts"));
  notes.append(
    el("p", { class: "panel-note" },
      "Assumptions are what the case takes as given. A flagged conflict is a " +
      "figure the team already believes its own sources disagree about; " +
      "flagging one lowers confidence rather than hiding it."),
  );
  notes.append(
    textField("Assumptions (one per line)", "assumptions",
      record.assumptions.join("\n"), 3),
  );
  const conflictTable = el("table");
  conflictTable.append(el("thead", {}, row("th", ["Figure", "What conflicts", ""])));
  const conflictBody = el("tbody", { id: "conflict-rows" });
  record.flagged_conflicts.forEach((conflict) => conflictBody.append(conflictRow(conflict)));
  conflictTable.append(conflictBody);
  notes.append(conflictTable);
  const addConflict = el("button", { type: "button" }, "Flag a conflict");
  addConflict.addEventListener("click", () => {
    conflictBody.append(conflictRow({ metric: state.schedule.schedule[0].metric, note: "" }));
  });
  notes.append(el("div", { class: "row-actions" }, addConflict));
  wrap.append(notes);

  const actions = el("div", { class: "actions" });
  const save = el("button", { class: "primary", type: "submit" }, "Save material");
  save.disabled = state.busy;
  actions.append(save);
  wrap.append(actions);

  wrap.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = readMaterial(wrap);
    act(async () => {
      state.detail = await api("POST", `/api/cases/${record.case_id}/material`, payload);
      await refreshCases();
      state.message = { kind: "info", text: "Material saved." };
      state.tab = "judgment";
    });
  });

  return wrap;
}

function sourceRow(source) {
  const tr = el("tr", { class: "source-row" });
  tr.append(
    el("td", {}, input("label", source.label, "SRC-AUDIT")),
    el("td", {}, input("origin", source.origin, "Independent audit of FY2024")),
    el("td", {}, select("kind", state.schedule.source_kinds, source.kind)),
  );
  const remove = el("button", { type: "button", class: "link" }, "Remove");
  remove.addEventListener("click", () => tr.remove());
  tr.append(el("td", {}, remove));
  return tr;
}

function conflictRow(conflict) {
  const tr = el("tr", { class: "conflict-row" });
  const metricOptions = state.schedule.schedule.map((entry) => ({
    key: entry.metric,
    label: entry.label,
  }));
  tr.append(
    el("td", {}, select("metric", metricOptions, conflict.metric)),
    el("td", {}, input("note", conflict.note, "Reference calls contradict the deck")),
  );
  const remove = el("button", { type: "button", class: "link" }, "Remove");
  remove.addEventListener("click", () => tr.remove());
  tr.append(el("td", {}, remove));
  return tr;
}

function figureRow(entry, figure) {
  const tr = el("tr", { class: "figure-row", "data-metric": entry.metric });
  const name = el("td", {});
  name.append(
    el("div", {}, entry.label),
    el("div", { class: "cites" }, `${entry.guidance} (${entry.unit})`),
  );
  tr.append(name);
  tr.append(el("td", { class: "numeric" }, input("value", figure ? figure.value : "", "")));
  tr.append(
    el("td", {}, select("status", state.schedule.figure_statuses,
      figure ? figure.status : "reported")),
  );

  const citeCell = el("td", { class: "cite-cell" });
  const selected = new Set(figure ? figure.source_labels : []);
  const labels = currentSourceLabels();
  if (!labels.length) {
    citeCell.append(el("span", { class: "cites" }, "Add a source first"));
  }
  labels.forEach((label) => {
    const wrapper = el("label", { class: "cites" });
    const box = el("input", { type: "checkbox", class: "cite-box", value: label });
    box.style.width = "auto";
    box.style.marginRight = "4px";
    if (selected.has(label)) box.checked = true;
    wrapper.append(box, label);
    citeCell.append(wrapper);
  });
  tr.append(citeCell);
  return tr;
}

function currentSourceLabels() {
  return state.detail.case.sources.map((source) => source.label).filter(Boolean);
}

function readMaterial(form) {
  const sources = Array.from(form.querySelectorAll(".source-row")).map((tr) => ({
    label: valueOf(tr, "label"),
    origin: valueOf(tr, "origin"),
    kind: valueOf(tr, "kind"),
  })).filter((source) => source.label);

  const figures = Array.from(form.querySelectorAll(".figure-row")).map((tr) => ({
    metric: tr.dataset.metric,
    value: valueOf(tr, "value"),
    status: valueOf(tr, "status"),
    source_labels: Array.from(tr.querySelectorAll(".cite-box:checked")).map((box) => box.value),
  })).filter((figure) => figure.value.trim());

  const conflicts = Array.from(form.querySelectorAll(".conflict-row")).map((tr) => ({
    metric: valueOf(tr, "metric"),
    note: valueOf(tr, "note"),
  })).filter((conflict) => conflict.note.trim());

  const assumptionsField = form.querySelector('[name="assumptions"]');
  const assumptions = assumptionsField.value.split("\n").map((line) => line.trim())
    .filter(Boolean);

  return { sources, figures, assumptions, flagged_conflicts: conflicts };
}

function valueOf(scope, name) {
  const node = scope.querySelector(`[name="${name}"]`);
  return node ? node.value : "";
}

function applyReference() {
  const record = state.detail.case;
  act(async () => {
    state.detail = await api("POST", `/api/cases/${record.case_id}/material`, state.reference);
    await refreshCases();
    state.message = {
      kind: "info",
      text:
        "Reference material loaded. This is the worked example carried by the " +
        "reference implementation; replace it with the real diligence pack.",
    };
  });
}

/* -------------------------------------------------------------- judgment */

function renderExecution() {
  const execution = state.execution;
  const panel = el("section", { class: "panel execution" });
  const running = execution.phase === "running";

  panel.append(
    el("h3", {}, running ? "Executing" : "Execution record"),
    el(
      "p",
      { class: "panel-note" },
      running
        ? "The engine is running. Stages are listed as they are reached in the " +
            "pipeline; nothing is reported until the run returns what it produced."
        : "What this run produced, in the order it was produced.",
    ),
  );

  if (running) {
    panel.append(el("div", { class: "execution-bar" }, el("span", {})));
  }

  const list = el("ol", { class: "execution-stages" });
  const stages = execution.stages.length
    ? execution.stages
    : PENDING_STAGE_LABELS.map((label) => ({ label }));

  stages.forEach((stage, index) => {
    const done = index < execution.revealed;
    // Only the row that just landed animates. The view is rebuilt on every
    // step, so animating every completed row would re-run the whole list each
    // time and read as flicker rather than as arrival.
    const latest = done && index === execution.revealed - 1;
    const row = el("li", {
      class: `execution-stage${latest ? " is-latest" : ""}`,
      "data-state": done ? "complete" : "pending",
    });
    row.append(
      el("span", { class: "execution-marker" }),
      el("span", { class: "execution-label" }, stage.label),
      el("span", { class: "execution-detail" }, done ? stage.detail || "" : ""),
    );
    list.append(row);
  });

  panel.append(list);
  return panel;
}

// Shown only while the request is open, so the panel is not an empty box. The
// labels match the stages the response is then read out against.
const PENDING_STAGE_LABELS = [
  "Material snapshot",
  "Document composed",
  "Reasoning record",
  "Review areas",
  "Cross-area positions",
  "Execution report",
];

function renderJudgment() {
  const record = state.detail.case;
  const judgment = state.detail.judgment;
  const wrap = el("div", {});

  // Mid-run and mid-reveal, the execution panel is the whole view. The
  // institutional decision appears only once every stage has been read out.
  if (state.execution && state.execution.phase !== "complete") {
    wrap.append(renderExecution());
    return wrap;
  }

  if (!judgment) {
    // `is-empty` opts this panel out of the uppercase-mono eyebrow treatment.
    // This heading is an empty-state title, not a section label.
    const panel = el("section", { class: "panel is-empty" });
    panel.append(el("h3", {}, "No judgment on file"));
    panel.append(
      el("p", { class: "panel-note" },
        "Nothing has been analysed for this case yet. The judgment is produced " +
        "from the material on file and can be reproduced from it exactly."),
    );
    const run = el("button", { class: "primary", type: "button" },
      "Request institutional judgment");
    run.disabled = state.busy || !record.sources.length || !record.figures.length;
    if (run.disabled && !state.busy) {
      panel.append(
        el("p", { class: "panel-note" },
          "Add at least one source and one figure on the Material tab first."),
      );
    }
    run.addEventListener("click", () => requestJudgment(record.case_id));
    panel.append(el("div", { class: "actions" }, run));
    wrap.append(panel);
    return wrap;
  }

  wrap.append(renderVerdict(judgment));
  // The completed record stays on screen under the decision. Every line in it
  // is evidence from this run, which is worth keeping beside the conclusion.
  if (state.execution && state.execution.phase === "complete") {
    wrap.append(renderExecution());
  }
  const history = renderJudgmentHistory();
  if (history) wrap.append(history);

  if (judgment.conditions.length) {
    const panel = el("section", { class: "panel" });
    panel.append(el("h3", {}, `Conditions (${judgment.conditions.length})`));
    panel.append(
      el("p", { class: "panel-note" },
        "Findings that support proceeding only if something is resolved first. " +
        "These are what a conditional approval would attach to."),
    );
    judgment.conditions.forEach((finding) => panel.append(findingBlock(finding)));
    wrap.append(panel);
  }

  if (judgment.disagreements.length) {
    const panel = el("section", { class: "panel" });
    panel.append(el("h3", {}, `Where the review areas disagree (${judgment.disagreements.length})`));
    panel.append(
      el("p", { class: "panel-note" },
        "Review areas cannot see each other's work, so a disagreement is a real " +
        "difference in what the material supports — not two passes at the same " +
        "answer."),
    );
    judgment.disagreements.forEach((view) => panel.append(topicBlock(view, true)));
    wrap.append(panel);
  }

  if (judgment.agreements.length) {
    const panel = el("section", { class: "panel" });
    panel.append(el("h3", {}, `Independent agreement (${judgment.agreements.length})`));
    panel.append(
      el("p", { class: "panel-note" },
        "Two review areas reaching the same conclusion without visibility of " +
        "each other."),
    );
    judgment.agreements.forEach((view) => panel.append(topicBlock(view, false)));
    wrap.append(panel);
  }

  const areas = el("section", { class: "panel" });
  areas.append(el("h3", {}, "Review areas"));
  const grid = el("div", { class: "area-grid" });
  judgment.review_areas.forEach((area) => grid.append(areaCard(area)));
  areas.append(grid);
  wrap.append(areas);

  if (judgment.unresolved_questions.length || judgment.outstanding_schedule_items.length) {
    const panel = el("section", { class: "panel" });
    panel.append(el("h3", {}, "What was not established"));
    panel.append(
      el("p", { class: "panel-note" },
        "Reported rather than absorbed. Nothing here was treated as a negative " +
        "finding."),
    );
    if (judgment.outstanding_schedule_items.length) {
      panel.append(el("h4", {}, "Figures not on file"));
      panel.append(list(judgment.outstanding_schedule_items));
    }
    if (judgment.unresolved_questions.length) {
      panel.append(el("h4", {}, "Questions the analysis could not close"));
      panel.append(list(judgment.unresolved_questions));
    }
    wrap.append(panel);
  }

  wrap.append(renderDecisionForm());
  return wrap;
}

function renderVerdict(judgment) {
  const box = el("section", { class: "verdict" });

  if (!judgment.is_current) {
    box.append(
      el(
        "p",
        { class: "superseded-banner" },
        `Superseded by ${judgment.superseded_by}. This is how the case read on ` +
          `${judgment.recorded_on}, kept unchanged so decisions taken against it ` +
          `stay defendable.`,
      ),
    );
  }

  box.append(el("h2", {}, judgment.recommendation));
  box.append(el("p", { class: "guidance" }, judgment.outcome_guidance));
  if (judgment.rationale.length) {
    box.append(list(judgment.rationale, "reason-list"));
  }
  const meta = el("div", { class: "verdict-meta" });
  meta.append(
    metric("Institutional confidence", judgment.confidence),
    metric("Limited by", judgment.confidence_note),
    metric("Judgment", `${judgment.judgment_id} · ${judgment.recorded_on}`),
    metric(
      "Material",
      judgment.snapshot_id
        ? `${judgment.snapshot_id} (v${judgment.material_version})`
        : "not identified",
    ),
  );
  box.append(meta);
  return box;
}

function renderJudgmentHistory() {
  const records = state.detail.case.judgments;
  if (records.length < 2) return null;

  const panel = el("section", { class: "panel" });
  panel.append(el("h3", {}, `Judgment history (${records.length})`));
  panel.append(
    el(
      "p",
      { class: "panel-note" },
      "Every analysis this case has reached, oldest first. A new analysis " +
        "supersedes the one before it and never replaces it — decisions keep " +
        "pointing at the judgment they were taken against.",
    ),
  );

  const viewing = state.detail.judgment ? state.detail.judgment.judgment_id : null;
  records.forEach((record, index) => {
    const row = el("div", { class: "position-row" });
    const open = el(
      "button",
      { class: "link", type: "button" },
      record.judgment_id === viewing
        ? `${record.judgment_id} (viewing)`
        : record.judgment_id,
    );
    open.addEventListener("click", () => viewJudgment(record.judgment_id));

    // Two judgments can reach the same conclusion from different material.
    // That is worth saying plainly: it means the committee deliberated again,
    // not that nothing happened.
    const previous = index > 0 ? records[index - 1] : null;
    let note = record.superseded_by
      ? `superseded by ${record.superseded_by}`
      : "in force";
    if (previous && previous.record_digest === record.record_digest) {
      note += " · same conclusion, different material";
    }

    row.append(
      open,
      el("span", { class: "numeric" }, `${record.recorded_on} · ${record.snapshot_id || "—"}`),
      el("span", { class: "cites" }, note),
    );
    panel.append(row);
  });
  return panel;
}

async function viewJudgment(judgmentId) {
  const caseId = state.detail.case.case_id;
  await act(async () => {
    state.detail = await api("GET", `/api/cases/${caseId}/judgments/${judgmentId}`);
    state.judgmentId = judgmentId;
  });
}

function areaCard(area) {
  const card = el("article", { class: "area" });
  const head = el("div", { class: "area-head" });
  head.append(
    el("h4", {}, area.review_area),
    el("span", { class: "metric-value" }, area.confidence),
  );
  card.append(head);
  card.append(el("p", { class: "cites" }, `${area.coverage} · limited by ${area.confidence_note}`));
  area.findings.forEach((finding) => card.append(findingBlock(finding)));
  if (area.unresolved_questions.length) {
    card.append(el("p", { class: "cites" },
      `${area.unresolved_questions.length} open question(s)`));
  }
  return card;
}

function findingBlock(finding) {
  const block = el("div", { class: "finding" });
  const head = el("p", {});
  head.append(
    el("span", { class: `stance is-${finding.stance.toLowerCase()}` }, finding.stance),
    el("span", { class: "finding-topic" }, finding.topic),
  );
  block.append(head);
  block.append(el("p", {}, finding.statement));
  if (finding.evidence_labels.length) {
    block.append(el("p", { class: "cites" }, `Cites: ${finding.evidence_labels.join("; ")}`));
  }
  return block;
}

function topicBlock(view, contested) {
  const block = el("div", { class: contested ? "disagreement" : "" });
  block.append(el("h4", {}, view.topic));
  view.positions.forEach(([area, stance, statement]) => {
    const line = el("div", { class: "position-row" });
    line.append(
      el("span", { class: "who" }, area),
      el("span", { class: `stance is-${stance.toLowerCase()}` }, stance),
      el("span", {}, statement),
    );
    block.append(line);
  });
  return block;
}

/* ------------------------------------------------------- staged execution

   What this is, and what it deliberately is not.

   The analysis runs as one synchronous request. The client therefore cannot
   observe the engine mid-flight, and this code never pretends otherwise:
   while the request is open, the panel shows the stages as *pending* and an
   indeterminate indicator. There is no percentage, because a percentage would
   be a number nobody measured.

   When the response lands, every artifact below is a fact on it. The panel
   then reads out as a completed execution record, in causal order, and each
   line carries evidence taken from the response — a snapshot id, a digest, a
   count. A stage is only ever displayed as complete, never as "now running",
   because we did not watch it run.

   One stage is genuinely sequential rather than paced: the execution report is
   a second real request, and it completes when the server answers.

   `REVEAL_STEP_MS` is presentation pacing for facts that are already true, not
   a measurement of anything. Under reduced motion the reveal is skipped
   entirely and every stage appears at once. */

const REVEAL_STEP_MS = 140;

function pause(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/* The stages, built from the response. Every detail string below is read off
   the payload; nothing here is computed for effect. */
function executionStages(detail) {
  const judgment = detail.judgment;
  const record = detail.case;
  const findings = judgment.review_areas.reduce(
    (total, area) => total + area.findings.length,
    0,
  );
  return [
    {
      label: "Material snapshot",
      detail: `${judgment.snapshot_id} · ${judgment.material_digest.slice(0, 16)}`,
    },
    {
      label: "Document composed",
      detail: `${record.sources.length} sources · ${record.figures.length} figures`,
    },
    {
      label: "Reasoning record",
      detail: judgment.record_digest.slice(0, 16),
    },
    {
      label: "Review areas",
      detail: `${judgment.review_areas.length} areas · ${findings} findings`,
    },
    {
      label: "Cross-area positions",
      detail:
        `${judgment.agreements.length} agreed · ` +
        `${judgment.disagreements.length} disagreed`,
    },
    {
      label: "Execution report",
      // Not paced — this stage completes when the server answers.
      resolve: async (caseId) => {
        const payload = await api("GET", `/api/cases/${caseId}/report`);
        return `${payload.report.split("\n").length} lines`;
      },
    },
  ];
}

async function revealExecution(caseId) {
  const stages = state.execution.stages;

  if (prefersReducedMotion()) {
    for (const stage of stages) {
      if (stage.resolve) {
        stage.detail = await stage.resolve(caseId).catch(() => "unavailable");
      }
    }
    state.execution.revealed = stages.length;
    state.execution.phase = "complete";
    render();
    return;
  }

  for (let index = 0; index < stages.length; index += 1) {
    const stage = stages[index];
    if (stage.resolve) {
      stage.detail = await stage.resolve(caseId).catch(() => "unavailable");
    } else {
      await pause(REVEAL_STEP_MS);
    }
    state.execution.revealed = index + 1;
    render();
  }

  // The institutional decision is the last thing to appear.
  if (!prefersReducedMotion()) await pause(REVEAL_STEP_MS);
  state.execution.phase = "complete";
  render();
}

async function requestJudgment(caseId) {
  // Synchronous, before the request is even sent: the panel is on screen by
  // the time the click finishes. Nothing is claimed about the engine yet.
  state.execution = { phase: "running", revealed: 0, stages: [] };
  state.message = null;
  state.tab = "judgment";
  state.busy = true;
  render();

  try {
    state.detail = await api("POST", `/api/cases/${caseId}/analysis`, {});
    state.judgmentId = null;
    await refreshCases();
    state.execution.stages = executionStages(state.detail);
    state.execution.phase = "revealing";
    state.busy = false;
    render();
    await revealExecution(caseId);
  } catch (error) {
    state.execution = null;
    state.message = { kind: "error", text: describe(error) };
    state.busy = false;
    render();
  }
}

function renderDecisionForm() {
  const panel = el("section", { class: "panel" });
  panel.append(el("h3", {}, "Record the committee decision"));

  // Decisions bind to the judgment in force. Recording one against a superseded
  // judgment would be minuting a meeting into the past.
  const judgment = state.detail.judgment;
  if (judgment && !judgment.is_current) {
    panel.append(
      el("p", { class: "panel-note" },
        `You are reading ${judgment.judgment_id}, which ${judgment.superseded_by} ` +
        "has superseded. Decisions are recorded against the judgment in force. " +
        "Open the current judgment to record one."),
    );
    return panel;
  }

  panel.append(
    el("p", { class: "panel-note" },
      "The decision is recorded against the judgment, not merged into it. A " +
      "committee that departs from the recommendation is the most important " +
      "thing this ledger can hold."),
  );

  const form = el("form", { class: "form-grid" });
  const decisions = [
    "Approved",
    "Approved with conditions",
    "Deferred pending further diligence",
    "Declined",
  ].map((label) => ({ key: label, label }));

  form.append(
    labelled("Decision", select("decision", decisions, "Approved with conditions")),
    field("Recorded by", "decided_by", ""),
    field("Date", "recorded_on", "", false, "date"),
    textField("Rationale", "rationale", "", 3),
  );

  const actions = el("div", { class: "actions wide" });
  const submit = el("button", { class: "primary", type: "submit" }, "Record decision");
  submit.disabled = state.busy;
  actions.append(submit);
  form.append(actions);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    act(async () => {
      state.detail = await api(
        "POST",
        `/api/cases/${state.detail.case.case_id}/decision`,
        {
          decision: data.get("decision"),
          decided_by: data.get("decided_by"),
          recorded_on: data.get("recorded_on"),
          rationale: data.get("rationale"),
        },
      );
      await refreshCases();
      state.tab = "overview";
      state.message = { kind: "info", text: "Decision recorded in the ledger." };
    });
  });

  panel.append(form);
  return panel;
}

/* ----------------------------------------------------------------- audit */

function renderAudit() {
  const wrap = el("div", {});
  const judgment = state.detail.judgment;

  const panel = el("section", { class: "panel" });
  panel.append(el("h3", {}, "Audit trail"));
  if (!judgment) {
    panel.append(el("p", { class: "panel-note" }, "Nothing has been analysed yet."));
    wrap.append(panel);
    return wrap;
  }
  panel.append(
    el("p", { class: "panel-note" },
      "This view exists so a decision can be defended. Everything below is the " +
      "reasoning record itself, not a description of it — re-running the same " +
      "material reproduces this digest exactly."),
  );
  panel.append(
    el("p", { class: "metric-label" },
      `${judgment.judgment_id} · recorded ${judgment.recorded_on}` +
        (judgment.is_current ? " · in force" : ` · superseded by ${judgment.superseded_by}`)),
  );
  panel.append(el("p", { class: "metric-label" }, "Record digest (SHA-256) — the reasoning"));
  panel.append(el("p", { class: "digest" }, judgment.record_digest));
  panel.append(
    el("p", { class: "metric-label" }, "Material digest (SHA-256) — what it was formed from"),
  );
  panel.append(
    el("p", { class: "digest" }, judgment.material_digest || "not identified"),
  );
  panel.append(
    el(
      "p",
      { class: "panel-note" },
      "Two separate claims. The record digest proves the reasoning; the " +
        "material digest proves what was reasoned over. The engine can reach " +
        "one conclusion from materially different packs, so the second does " +
        "not follow from the first.",
    ),
  );
  wrap.append(panel);

  const reportPanel = el("section", { class: "panel" });
  reportPanel.append(el("h3", {}, "Full reasoning record"));
  const holder = el("pre", { class: "report-text" }, "Loading…");
  reportPanel.append(holder);
  wrap.append(reportPanel);

  const reportPath = state.judgmentId
    ? `/api/cases/${state.detail.case.case_id}/judgments/${state.judgmentId}/report`
    : `/api/cases/${state.detail.case.case_id}/report`;
  api("GET", reportPath)
    .then((payload) => {
      holder.textContent = payload.report;
    })
    .catch((error) => {
      holder.textContent = describe(error);
    });

  return wrap;
}

/* ----------------------------------------------------------- dom helpers */

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  Object.entries(attrs || {}).forEach(([key, value]) => {
    if (key === "style") {
      node.setAttribute("style", value);
    } else if (value !== undefined && value !== null && value !== "") {
      node.setAttribute(key, value);
    }
  });
  children.flat().forEach((child) => {
    if (child === null || child === undefined) return;
    node.append(child);
  });
  return node;
}

function row(cell, values) {
  const tr = el("tr", {});
  values.forEach((value) => tr.append(el(cell, {}, value)));
  return tr;
}

function list(values, className) {
  const ul = el("ul", { class: className || "plain" });
  values.forEach((value) => ul.append(el("li", {}, value)));
  return ul;
}

function metric(label, value) {
  const box = el("div", {});
  box.append(
    el("span", { class: "metric-label" }, label),
    el("span", { class: "metric-value" }, value),
  );
  return box;
}

function labelled(text, control) {
  const label = el("label", {});
  label.append(el("span", { class: "field-label" }, text), control);
  return label;
}

function field(text, name, value, wide, type) {
  const label = labelled(text, input(name, value, "", type));
  if (wide) label.classList.add("wide");
  return label;
}

function textField(text, name, value, rows) {
  const area = el("textarea", { name, rows: String(rows || 3) });
  area.value = value || "";
  const label = labelled(text, area);
  label.classList.add("wide");
  return label;
}

function input(name, value, placeholder, type) {
  const node = el("input", {
    name,
    type: type || "text",
    placeholder: placeholder || "",
    class: "compact",
  });
  node.value = value || "";
  return node;
}

function select(name, options, selected) {
  const node = el("select", { name, class: "compact" });
  options.forEach((option) => {
    const item = el("option", { value: option.key }, option.label);
    if (option.key === selected) item.selected = true;
    node.append(item);
  });
  return node;
}
