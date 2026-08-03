/*
 * Product prototype interaction layer for the investment prototype UI.
 *
 * The completed workspace still operates on browser memory and fixtures from
 * fixtures.js. The optional Risk RIK panel calls only the local
 * prototype_risk_rik development endpoint; it does not call DAALE modules,
 * production APIs, persistence systems, orchestration layers, or schedulers.
 */

const fixtures = window.YUKTI_INVESTMENT_FIXTURES;

const state = {
  cases: fixtures.cases.map((investmentCase) => structuredClone(investmentCase)),
  selectedCaseId: fixtures.cases[0].caseId,
  selectedLedgerId: fixtures.cases[0].decisionLedger[0].id,
  showingIntake: false,
  riskRik: {
    byCaseId: {},
    provider: {
      provider: "unknown",
      mode: "unknown",
      configured: false,
      requires_credentials: false,
      description: "Provider status has not been loaded.",
    },
  },
};

const caseList = document.querySelector("#case-list");
const caseWorkspace = document.querySelector("#case-workspace");
const intakePanel = document.querySelector("#intake-panel");
const caseForm = document.querySelector("#case-form");
const newCaseButton = document.querySelector("#new-case-button");
const cancelIntakeButton = document.querySelector("#cancel-intake-button");
const cardTemplate = document.querySelector("#case-card-template");

newCaseButton.addEventListener("click", () => {
  state.showingIntake = true;
  render();
});

cancelIntakeButton.addEventListener("click", () => {
  state.showingIntake = false;
  render();
});

caseForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(caseForm);
  const createdCase = createDraftCase(formData);
  state.cases = [createdCase, ...state.cases];
  state.selectedCaseId = createdCase.caseId;
  state.selectedLedgerId = null;
  state.showingIntake = false;
  caseForm.reset();
  render();
});

function createDraftCase(formData) {
  const now = new Date();
  const company = readFormValue(formData, "company", "New company");
  const defaults = fixtures.blankCaseDefaults;

  return {
    ...defaults,
    caseId: `mock-draft-${now.getTime()}`,
    title: `${company} Investment Case`,
    company,
    ticker: readFormValue(formData, "ticker", defaults.ticker),
    sector: readFormValue(formData, "sector", defaults.sector),
    createdAt: now.toISOString().slice(0, 10),
    requestedDecision: readFormValue(
      formData,
      "requestedDecision",
      defaults.requestedDecision,
    ),
    investmentThesis: readFormValue(
      formData,
      "investmentThesis",
      defaults.investmentThesis,
    ),
    status: {
      overall: "Draft",
      rik: [
        {
          name: "Analysis setup",
          state: "Not started",
          owner: "Mock UI",
          summary:
            "No institutional analysis has been generated for this user-created case.",
        },
      ],
    },
    evidence: [],
    rikPositions: [],
    contestedPropositions: [],
    decisionLedger: [],
    investmentConditions: [],
    unresolvedQuestions: [],
    decision: null,
  };
}

function readFormValue(formData, name, fallback) {
  const value = String(formData.get(name) || "").trim();
  return value || fallback;
}

function render() {
  renderCaseList();
  renderIntake();
  renderWorkspace();
}

async function loadProviderStatus() {
  if (window.location.protocol === "file:") {
    state.riskRik.provider = {
      provider: "static file",
      mode: "fixture-only browsing",
      configured: false,
      requires_credentials: false,
      description:
        "Open the local prototype server to run deterministic or live Risk RIK execution.",
    };
    render();
    return;
  }

  try {
    const response = await fetch("/prototype-risk-rik/provider");
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Provider status unavailable.");
    }
    state.riskRik.provider = payload.provider;
  } catch (error) {
    state.riskRik.provider = {
      provider: "unavailable",
      mode: "provider status unavailable",
      configured: false,
      requires_credentials: false,
      description: error instanceof Error ? error.message : String(error),
    };
  }
  render();
}

function renderCaseList() {
  caseList.replaceChildren();
  for (const investmentCase of state.cases) {
    const fragment = cardTemplate.content.cloneNode(true);
    const button = fragment.querySelector(".case-card");
    const title = fragment.querySelector(".case-card-title");
    const meta = fragment.querySelector(".case-card-meta");

    button.classList.toggle("active", investmentCase.caseId === state.selectedCaseId);
    button.addEventListener("click", () => {
      state.selectedCaseId = investmentCase.caseId;
      state.selectedLedgerId = firstLedgerId(investmentCase);
      state.showingIntake = false;
      render();
    });
    title.textContent = investmentCase.title;
    meta.textContent = `${investmentCase.stage} - ${investmentCase.createdAt}`;
    caseList.append(fragment);
  }
}

function firstLedgerId(investmentCase) {
  return investmentCase.decisionLedger?.[0]?.id || null;
}

function renderIntake() {
  intakePanel.classList.toggle("hidden", !state.showingIntake);
}

function renderWorkspace() {
  const investmentCase = selectedCase();
  if (!state.selectedLedgerId) {
    state.selectedLedgerId = firstLedgerId(investmentCase);
  }
  caseWorkspace.replaceChildren(renderCaseWorkspace(investmentCase));
}

function selectedCase() {
  return (
    state.cases.find((investmentCase) => investmentCase.caseId === state.selectedCaseId) ||
    state.cases[0]
  );
}

function renderCaseWorkspace(investmentCase) {
  const container = el("div", "stack");
  container.append(
    renderOverview(investmentCase),
    renderPrototypeRiskRikPanel(investmentCase),
  );

  if (!hasCompletedGraph(investmentCase)) {
    container.append(renderInstitutionalAnalysisNotGenerated(investmentCase));
    return container;
  }

  container.append(renderReasoningWorkspace(investmentCase));
  return container;
}

function hasCompletedGraph(investmentCase) {
  return Boolean(investmentCase.decision && investmentCase.decisionLedger?.length);
}

function renderOverview(investmentCase) {
  const card = el("section", "workspace-card");
  const header = el("div", "workspace-header");
  const titleBlock = el("div");
  titleBlock.append(
    textEl("p", "eyebrow", "Case Workspace"),
    textEl("h2", "", investmentCase.title),
    textEl("p", "muted", investmentCase.investmentThesis),
  );

  header.append(titleBlock);

  const badges = el("div", "badge-row");
  badges.append(
    textEl(
      "span",
      `badge ${hasCompletedGraph(investmentCase) ? "complete" : "draft"}`,
      hasCompletedGraph(investmentCase) ? "Completed reasoning fixture" : "Draft",
    ),
    textEl("span", "badge", investmentCase.investmentType),
    textEl("span", "badge", investmentCase.timeHorizon),
    textEl("span", "badge", investmentCase.sector),
  );

  const metrics = el("div", "grid");
  metrics.append(
    metric("Company", `${investmentCase.company} (${investmentCase.ticker})`),
    metric("Requested decision", investmentCase.requestedDecision),
    metric("Mandate fit", investmentCase.mandateFit),
    metric(
      "Prototype boundary",
      hasCompletedGraph(investmentCase)
        ? "Fixture analysis is predefined; Risk RIK execution results are separate"
        : "Only explicitly entered case data is shown",
    ),
  );

  card.append(header, badges, metrics);
  return card;
}

function renderInstitutionalAnalysisNotGenerated(investmentCase) {
  const card = el("section", "workspace-card");
  card.append(
    textEl("p", "eyebrow", "User-Created Case State"),
    textEl("h3", "", "Institutional Analysis Not Generated"),
    textEl(
      "p",
      "muted",
      "The current executable prototype runs only the Risk RIK. Multi-RIK analysis, conflict resolution, and institutional decision construction are not connected to this case.",
    ),
    textEl(
      "p",
      "muted",
      investmentCase.evidence?.length
        ? "Structured evidence has been attached to this case."
        : "No structured evidence has been attached to this case.",
    ),
  );

  const list = el("ul", "plain-list");
  for (const question of investmentCase.keyQuestions) {
    list.append(textEl("li", "", question));
  }
  card.append(list);
  return card;
}

function renderPrototypeRiskRikPanel(investmentCase) {
  const execution = state.riskRik.byCaseId[investmentCase.caseId] || {
    status: "idle",
    artifact: null,
    error: "",
  };
  const section = el("section", "workspace-card prototype-execution");
  const header = el("div", "workspace-header");
  const titleBlock = el("div");
  titleBlock.append(
    textEl("p", "eyebrow", "Prototype Execution"),
    textEl("h3", "", "Run Risk RIK"),
    textEl(
      "p",
      "muted",
      "Executes only the prototype Risk RIK against supplied case material. It does not update the fixture analysis or generate an institutional decision.",
    ),
  );
  header.append(titleBlock, textEl("span", "badge draft", "Executable path"));
  section.append(header);
  section.append(renderProviderStatus(execution.provider || state.riskRik.provider));

  const form = el("form", "risk-rik-form");
  form.addEventListener("submit", (event) => {
    void runRiskRikFromForm(event, investmentCase);
  });

  form.append(
    labeledTextarea(
      "Case Material",
      "case_material",
      buildDefaultCaseMaterial(investmentCase),
      8,
      true,
    ),
    labeledInput("Evidence Source Label (optional)", "source_label", "", false),
    labeledTextarea(
      "Evidence Source Text (optional)",
      "source_text",
      "",
      6,
      false,
    ),
  );

  const actions = el("div", "form-actions wide");
  const submitButton = el(
    "button",
    "",
    execution.status === "running" ? "Running Risk RIK" : "Run Prototype Risk RIK",
  );
  submitButton.type = "submit";
  submitButton.disabled = execution.status === "running";
  actions.append(submitButton);
  form.append(actions);
  section.append(form);

  if (execution.error) {
    section.append(textEl("p", "execution-error", execution.error));
  }

  if (execution.artifact) {
    section.append(renderPrototypeExecutionResult(execution));
  }

  return section;
}

function buildDefaultCaseMaterial(investmentCase) {
  const evidenceSummary = investmentCase.evidence?.length
    ? investmentCase.evidence
        .slice(0, 6)
        .map((item) => `${item.title}: ${item.extractedFact}`)
        .join("\n")
    : "";

  return [
    `Company: ${investmentCase.company}`,
    `Requested decision: ${investmentCase.requestedDecision}`,
    `Investment thesis: ${investmentCase.investmentThesis}`,
    evidenceSummary ? `Evidence summary:\n${evidenceSummary}` : "",
  ]
    .filter(Boolean)
    .join("\n\n");
}

function labeledInput(labelText, name, value, required) {
  const label = el("label");
  const input = el("input");
  input.name = name;
  input.value = value;
  input.required = required;
  label.append(document.createTextNode(labelText), input);
  return label;
}

function labeledTextarea(labelText, name, value, rows, required) {
  const label = el("label", "wide");
  const textarea = el("textarea");
  textarea.name = name;
  textarea.rows = rows;
  textarea.value = value;
  textarea.required = required;
  label.append(document.createTextNode(labelText), textarea);
  return label;
}

async function runRiskRikFromForm(event, investmentCase) {
  event.preventDefault();

  if (window.location.protocol === "file:") {
    state.riskRik.byCaseId[investmentCase.caseId] = {
      status: "error",
      artifact: null,
      error:
        "Start the local prototype server with: python -m applications.investment.prototype_risk_rik.server",
      provider: state.riskRik.provider,
    };
    render();
    return;
  }

  const formData = new FormData(event.currentTarget);
  const caseMaterial = readFormValue(formData, "case_material", "");
  const sourceLabel = String(formData.get("source_label") || "").trim();
  const sourceText = readFormValue(formData, "source_text", "");
  if (sourceText && !sourceLabel) {
    state.riskRik.byCaseId[investmentCase.caseId] = {
      status: "error",
      artifact: null,
      error: "Evidence source text requires an explicit source label.",
      provider: state.riskRik.provider,
    };
    render();
    return;
  }

  const sourceMaterials = sourceText
    ? [
        {
          label: sourceLabel,
          text: sourceText,
        },
      ]
    : [];

  state.riskRik.byCaseId[investmentCase.caseId] = {
    status: "running",
    artifact: null,
    error: "",
    provider: state.riskRik.provider,
  };
  render();

  try {
    const response = await fetch("/prototype-risk-rik/execute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        case_title: investmentCase.title,
        case_material: caseMaterial,
        source_materials: sourceMaterials,
      }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "Prototype Risk RIK execution failed.");
    }

    state.riskRik.byCaseId[investmentCase.caseId] = {
      status: "complete",
      artifact: payload.artifact,
      error: "",
      provider: payload.provider || state.riskRik.provider,
    };
  } catch (error) {
    state.riskRik.byCaseId[investmentCase.caseId] = {
      status: "error",
      artifact: null,
      error: error instanceof Error ? error.message : String(error),
      provider: state.riskRik.provider,
    };
  }

  render();
}

function renderProviderStatus(provider) {
  const status = el(
    "div",
    `provider-status ${provider.configured ? "configured" : "not-configured"}`,
  );
  status.append(
    textEl("strong", "", `Provider: ${provider.provider}`),
    textEl("span", "", `Mode: ${provider.mode}`),
    textEl("span", "", provider.description),
  );
  return status;
}

function renderPrototypeExecutionResult(execution) {
  const artifact = execution.artifact;
  const provider = execution.provider || state.riskRik.provider;
  const wrapper = el("article", "prototype-result");
  wrapper.append(
    textEl("p", "eyebrow", "Prototype Execution Result"),
    textEl("h3", "", executionModeTitle(provider)),
    textEl("p", "item-copy", executionProvenanceCopy(provider)),
  );

  const resultMetrics = el("div", "grid compact-grid");
  resultMetrics.append(
    metric("Run ID", artifact.run_id),
    metric("Provider", provider.provider),
    metric("Execution mode", provider.mode),
    metric("RIK identity", artifact.rik_identity),
    metric("Confidence", artifact.qualitative_confidence),
  );
  wrapper.append(resultMetrics, renderRiskRikArtifact(artifact));
  return wrapper;
}

function executionModeTitle(provider) {
  if (provider.provider === "deterministic") {
    return "Deterministic Development Execution";
  }
  if (provider.configured && provider.requires_credentials) {
    return "Live Model Execution";
  }
  return "Prototype Execution";
}

function executionProvenanceCopy(provider) {
  if (provider.provider === "deterministic") {
    return "This result was generated by the rule-based development provider to exercise the YUKTI execution pipeline. It is not live model reasoning.";
  }
  return provider.description;
}

function renderRiskRikArtifact(artifact) {
  const wrapper = el("div", "validated-artifact");
  wrapper.append(
    textEl("p", "eyebrow", "Validated Risk RIK Artifact"),
    textEl("h4", "", artifact.primary_conclusion),
    textEl(
      "p",
      "status-line",
      `${artifact.rik_identity} - ${artifact.run_id} - ${artifact.qualitative_confidence}`,
    ),
  );

  const grid = el("div", "artifact-grid");
  grid.append(
    artifactList(
      "Identified risks",
      artifact.identified_risks.map(
        (risk) =>
          `${risk.severity}: ${risk.name} - ${risk.description} Condition: ${risk.mitigation_or_condition}`,
      ),
    ),
    artifactList(
      "Relevant propositions",
      artifact.relevant_propositions.map(
        (item) => `${item.position}: ${item.proposition} - ${item.reasoning_summary}`,
      ),
    ),
    artifactList("Key assumptions", artifact.key_assumptions),
    artifactList("Information that would change position", artifact.information_that_would_change_position),
    artifactList("Unresolved questions", artifact.unresolved_questions),
    artifactList(
      "Evidence references",
      artifact.evidence_references.map(
        (item) => `${item.source_label}: ${item.support_status} - ${item.relevance}`,
      ),
    ),
  );
  wrapper.append(grid);
  wrapper.append(
    textEl("p", "item-copy", `Strongest objection: ${artifact.strongest_objection}`),
  );
  return wrapper;
}

function artifactList(title, values) {
  const wrapper = el("div", "detail-list");
  wrapper.append(textEl("strong", "", title));
  const list = el("ul", "plain-list compact");
  for (const value of values.filter(Boolean)) {
    list.append(textEl("li", "", value));
  }
  if (!list.children.length) {
    list.append(textEl("li", "", "None supplied."));
  }
  wrapper.append(list);
  return wrapper;
}

function renderReasoningWorkspace(investmentCase) {
  const wrapper = el("div", "stack");
  wrapper.append(renderFixtureBoundary(), renderDecisionSummary(investmentCase));

  const selectedLedger = currentLedger(investmentCase);
  const related = relatedIdsForLedger(investmentCase, selectedLedger);

  const traceGrid = el("div", "trace-grid");
  traceGrid.append(
    renderDecisionLedger(investmentCase, selectedLedger),
    renderTraceInspector(investmentCase, selectedLedger, related),
  );

  wrapper.append(
    traceGrid,
    renderConflicts(investmentCase, selectedLedger),
    renderRikPositions(investmentCase, related.rikIds),
    renderEvidenceLayer(investmentCase, related.evidenceIds),
    renderUnresolvedQuestions(investmentCase, related.propositionId),
  );

  return wrapper;
}

function renderFixtureBoundary() {
  const section = el("section", "workspace-card fixture-boundary");
  section.append(
    textEl("p", "eyebrow", "Predefined Demonstration Data"),
    textEl("h3", "", "Fixture Institutional Analysis"),
    textEl(
      "p",
      "muted",
      "Predefined demonstration data used to prototype YUKTI's institutional reasoning interface. This analysis was not generated by the current executable Risk RIK pipeline.",
    ),
  );
  return section;
}

function renderDecisionSummary(investmentCase) {
  const card = el("section", "decision-summary");
  const decision = investmentCase.decision;
  card.append(
    textEl("p", "eyebrow", "Institutional Judgment"),
    textEl("h3", "", decision.outcome),
    textEl("p", "decision-strength", `Decision Strength: ${decision.decisionStrength}`),
    textEl("p", "item-copy", decision.rationale),
  );

  const path = el("div", "reasoning-path");
  for (const label of [
    "Decision Ledger",
    "Contested Proposition",
    "RIK Positions",
    "Evidence",
  ]) {
    path.append(textEl("span", "", label));
  }
  card.append(path);
  return card;
}

function currentLedger(investmentCase) {
  return (
    investmentCase.decisionLedger.find((entry) => entry.id === state.selectedLedgerId) ||
    investmentCase.decisionLedger[0]
  );
}

function relatedIdsForLedger(investmentCase, ledger) {
  const conflict = conflictById(investmentCase, ledger.conflictId);
  const conflictEvidence = conflict.positions.flatMap((position) => position.evidence);
  const rikEvidence = ledger.rikPositions.flatMap((rikId) => {
    const position = rikById(investmentCase, rikId);
    return position ? position.decisiveEvidence : [];
  });

  return {
    propositionId: ledger.conflictId,
    rikIds: uniqueStrings([...ledger.rikPositions, ...conflict.positions.map((p) => p.rikId)]),
    evidenceIds: uniqueStrings([
      ...ledger.decisiveEvidence,
      ...conflictEvidence,
      ...rikEvidence,
    ]),
  };
}

function uniqueStrings(values) {
  return [...new Set(values.filter(Boolean))];
}

function renderDecisionLedger(investmentCase, selectedLedger) {
  const section = el("section", "workspace-card");
  section.append(
    textEl("p", "eyebrow", "Layer 4"),
    textEl("h3", "", "Decision Ledger"),
    textEl(
      "p",
      "muted",
      "Select an institutional decision proposition to trace it backward.",
    ),
  );

  const list = el("div", "ledger-list");
  for (const entry of investmentCase.decisionLedger) {
    const button = el(
      "button",
      `ledger-entry ${entry.id === selectedLedger.id ? "selected" : ""}`,
    );
    button.type = "button";
    button.addEventListener("click", () => {
      state.selectedLedgerId = entry.id;
      render();
    });
    button.append(
      textEl("span", "object-id", entry.id),
      textEl("strong", "", entry.title),
      textEl("span", "position-label", entry.institutionalPosition),
      textEl("span", "muted", entry.reason),
    );
    list.append(button);
  }
  section.append(list);
  return section;
}

function renderTraceInspector(investmentCase, ledger, related) {
  const conflict = conflictById(investmentCase, ledger.conflictId);
  const condition = conditionById(investmentCase, ledger.conditionId);
  const section = el("section", "workspace-card trace-inspector");
  section.append(
    textEl("p", "eyebrow", "Trace Inspector"),
    textEl("h3", "", ledger.title),
  );

  const ordered = el("ol", "trace-steps");
  ordered.append(
    traceStep(
      "Decision",
      `${ledger.institutionalPosition} - ${ledger.reason}`,
      [ledger.id],
    ),
    traceStep(
      "Contested proposition",
      `${conflict.id}: ${conflict.proposition}`,
      [conflict.status],
    ),
    traceStep(
      "Competing RIK positions",
      related.rikIds
        .map((rikId) => {
          const rik = rikById(investmentCase, rikId);
          const conflictPosition = conflict.positions.find((item) => item.rikId === rikId);
          return `${rik.name}: ${conflictPosition?.stance || "RELATED"}`;
        })
        .join("; "),
      related.rikIds,
    ),
    traceStep(
      "Evidence",
      related.evidenceIds
        .map((evidenceId) => evidenceById(investmentCase, evidenceId).title)
        .join("; "),
      related.evidenceIds,
    ),
  );
  section.append(ordered);

  const uncertainty = el("div", "trace-note");
  uncertainty.append(
    textEl("strong", "", "Remaining uncertainty"),
    textEl("p", "", ledger.remainingUncertainty),
  );
  section.append(uncertainty);

  if (condition) {
    const conditionBlock = el("div", "trace-note");
    conditionBlock.append(
      textEl("strong", "", "Resulting condition"),
      textEl("p", "", `${condition.id}: ${condition.text}`),
    );
    section.append(conditionBlock);
  }

  return section;
}

function traceStep(label, copy, tags) {
  const item = el("li", "");
  const tagRow = el("div", "tag-row");
  for (const tag of tags) {
    tagRow.append(textEl("span", "mini-tag", tag));
  }
  item.append(textEl("strong", "", label), textEl("p", "", copy), tagRow);
  return item;
}

function renderConflicts(investmentCase, selectedLedger) {
  const section = el("section", "workspace-card");
  section.append(
    textEl("p", "eyebrow", "Layer 3"),
    textEl("h3", "", "Contested Propositions"),
  );

  const grid = el("div", "conflict-grid");
  for (const conflict of investmentCase.contestedPropositions) {
    const relatedLedger = investmentCase.decisionLedger.find(
      (entry) => entry.conflictId === conflict.id,
    );
    const card = el(
      "article",
      `conflict-card ${selectedLedger.conflictId === conflict.id ? "highlight" : ""}`,
    );
    card.append(
      textEl("p", "object-id", conflict.id),
      textEl("h4", "", conflict.theme),
      textEl("p", "item-copy", conflict.proposition),
      textEl("p", "status-line", `Status: ${conflict.status}`),
      textEl("p", "muted", conflict.summary),
    );

    if (relatedLedger) {
      const focusButton = el("button", "secondary small-button", "Focus decision");
      focusButton.type = "button";
      focusButton.addEventListener("click", () => {
        state.selectedLedgerId = relatedLedger.id;
        render();
      });
      card.append(focusButton);
    }
    grid.append(card);
  }

  section.append(grid);
  return section;
}

function renderRikPositions(investmentCase, activeRikIds) {
  const section = el("section", "workspace-card");
  section.append(
    textEl("p", "eyebrow", "Layer 2"),
    textEl("h3", "", "Independent RIK Positions"),
    textEl(
      "p",
      "muted",
      "These are inspectable fixture positions, not executed agents or AI personas.",
    ),
  );

  const grid = el("div", "rik-grid");
  for (const rik of investmentCase.rikPositions) {
    const active = activeRikIds.includes(rik.id);
    const card = el("article", `rik-card ${active ? "highlight" : ""}`);
    card.append(
      textEl("p", "object-id", rik.id),
      textEl("h4", "", rik.name),
      textEl("p", "status-line", `${rik.domain} - ${rik.status} - ${rik.confidence}`),
      textEl("p", "item-copy", rik.primaryConclusion),
      detailList("Key assumptions", rik.assumptions),
      detailList("Decisive evidence", rik.decisiveEvidence),
      textEl("p", "item-copy", `Strongest objection: ${rik.strongestObjection}`),
      textEl("p", "item-copy", `Would change position: ${rik.changeEvidence}`),
    );
    rikGridAppendRelatedPropositions(card, rik.relatedPropositions);
    grid.append(card);
  }

  section.append(grid);
  return section;
}

function rikGridAppendRelatedPropositions(card, propositionIds) {
  const row = el("div", "tag-row");
  for (const id of propositionIds) {
    row.append(textEl("span", "mini-tag", id));
  }
  card.append(row);
}

function renderEvidenceLayer(investmentCase, activeEvidenceIds) {
  const section = el("section", "workspace-card");
  section.append(
    textEl("p", "eyebrow", "Layer 1"),
    textEl("h3", "", "Evidence Layer"),
    textEl(
      "p",
      "muted",
      "The evidence layer separates known facts, management claims, analyst inferences, and missing or unresolved information.",
    ),
  );

  const buckets = [
    ["Known", "What is known"],
    ["Claimed", "What is claimed"],
    ["Inferred", "What is inferred"],
    ["Missing", "What is missing or unresolved"],
  ];

  const grid = el("div", "evidence-buckets");
  for (const [bucketKey, title] of buckets) {
    const bucket = el("section", "evidence-bucket");
    bucket.append(textEl("h4", "", title));
    const items = investmentCase.evidence.filter(
      (item) => item.knownClaimedInferred === bucketKey,
    );

    if (!items.length) {
      bucket.append(emptyState("No fixture evidence in this category."));
    } else {
      for (const item of items) {
        bucket.append(renderEvidenceItem(item, activeEvidenceIds.includes(item.id)));
      }
    }
    grid.append(bucket);
  }

  section.append(grid);
  return section;
}

function renderEvidenceItem(item, active) {
  const card = el("article", `evidence-card ${active ? "highlight" : ""}`);
  card.append(
    textEl("p", "object-id", item.id),
    textEl("h5", "", item.title),
    textEl(
      "p",
      "status-line",
      `${item.classification} - ${item.quality} quality - ${item.date}`,
    ),
    textEl("p", "item-copy", item.extractedFact),
    textEl("p", "muted", `${item.sourceType}: ${item.source}`),
    textEl("p", "muted", item.provenance),
  );

  const referencedBy = el("div", "tag-row");
  for (const id of [...item.references.propositions, ...item.references.rikPositions]) {
    referencedBy.append(textEl("span", "mini-tag", id));
  }
  card.append(referencedBy);
  return card;
}

function renderUnresolvedQuestions(investmentCase, activePropositionId) {
  const section = el("section", "workspace-card");
  section.append(
    textEl("p", "eyebrow", "Open Items"),
    textEl("h3", "", "Unresolved Questions"),
  );

  const list = el("ul", "question-list");
  for (const item of investmentCase.unresolvedQuestions) {
    const active = item.relatedPropositions.includes(activePropositionId);
    const listItem = el("li", `question-item ${active ? "highlight" : ""}`);
    listItem.append(
      textEl("p", "item-title", `${item.id}: ${item.question}`),
      textEl("p", "item-copy", `${item.severity} severity`),
    );
    const row = el("div", "tag-row");
    for (const id of [...item.relatedPropositions, ...item.relatedEvidence]) {
      row.append(textEl("span", "mini-tag", id));
    }
    listItem.append(row);
    list.append(listItem);
  }

  section.append(list);
  return section;
}

function detailList(title, values) {
  const wrapper = el("div", "detail-list");
  wrapper.append(textEl("strong", "", title));
  const list = el("ul", "plain-list compact");
  for (const value of values) {
    list.append(textEl("li", "", value));
  }
  wrapper.append(list);
  return wrapper;
}

function conflictById(investmentCase, id) {
  return investmentCase.contestedPropositions.find((item) => item.id === id);
}

function rikById(investmentCase, id) {
  return investmentCase.rikPositions.find((item) => item.id === id);
}

function evidenceById(investmentCase, id) {
  return investmentCase.evidence.find((item) => item.id === id);
}

function conditionById(investmentCase, id) {
  return investmentCase.investmentConditions.find((item) => item.id === id);
}

function metric(label, value) {
  const item = el("div", "metric");
  item.append(textEl("span", "", label), textEl("strong", "", value));
  return item;
}

function emptyState(message) {
  return textEl("p", "muted", message);
}

function el(tagName, className = "", text = "") {
  const node = document.createElement(tagName);
  if (className) {
    node.className = className;
  }
  if (text) {
    node.textContent = text;
  }
  return node;
}

function textEl(tagName, className, text) {
  return el(tagName, className, text);
}

render();
void loadProviderStatus();
