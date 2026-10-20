/* The conversational surface.
 *
 * A chat bar over the same JSON interface the record view uses. It does three
 * things and refuses the rest:
 *
 *   1. reads pasted prose into *proposed* figures you confirm one by one
 *   2. runs the engine on the material you confirmed
 *   3. answers questions out of the reasoning record
 *
 * A language model is optional and, when configured, does exactly two things:
 * it reads messier prose into the same unconfirmed proposals, and it puts an
 * answer the record already computed into better words. It never decides, never
 * commits, and is checked afterwards — a phrased answer carrying a figure the
 * record does not contain is thrown away and the computed answer shown instead.
 *
 * So every reply here is still a fact about the case store or a projection of
 * the record on disk, and can be checked against the artifact rather than
 * believed. Each one says which path produced it. When the chat does not
 * understand something it says so rather than improvising — the same discipline
 * as a judgment that declines.
 */

const state = {
  cases: [],
  caseId: null,
  detail: null,
  schedule: null,
  messages: [],
  busy: false,
  booting: true,
  pending: null, // an in-flight guided flow: intake or decision
};

const thread = document.getElementById("thread");
const chips = document.getElementById("chips");
const form = document.getElementById("composer-form");
const input = document.getElementById("composer-input");
const sendButton = document.getElementById("composer-send");
const picker = document.getElementById("case-picker");
const contextLabel = document.getElementById("chat-context");
const recordLink = document.getElementById("record-link");

/* ------------------------------------------------------------------ dom */

function el(tag, attributes, ...children) {
  const node = document.createElement(tag);
  Object.entries(attributes || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined) node.setAttribute(key, value);
  });
  children.flat().forEach((child) => {
    if (child === null || child === undefined || child === false) return;
    node.append(child instanceof Node ? child : document.createTextNode(child));
  });
  return node;
}

/* Minimal inline formatting: **bold** and paragraph/bullet structure. The
   answers come from `explain.py`, which writes exactly this much markup. */
function richText(text) {
  const box = el("div", { class: "rich" });
  String(text)
    .split("\n")
    .forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed) {
        box.append(el("div", { class: "rich-gap" }));
        return;
      }
      const isBullet = trimmed.startsWith("- ");
      const body = isBullet ? trimmed.slice(2) : trimmed;
      const row = el("p", { class: isBullet ? "rich-line is-bullet" : "rich-line" });
      body.split(/(\*\*[^*]+\*\*)/).forEach((part) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          row.append(el("strong", {}, part.slice(2, -2)));
        } else if (part) {
          row.append(document.createTextNode(part));
        }
      });
      box.append(row);
    });
  return box;
}

/* ----------------------------------------------------------- transport */

async function api(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

/* --------------------------------------------------------- transcript */

function say(role, content, options) {
  state.messages.push({ role, content, ...(options || {}) });
  render();
}

function scrollDown() {
  thread.scrollTop = thread.scrollHeight;
}

function render() {
  renderHeader();
  renderThread();
  renderChips();
  sendButton.disabled = state.busy;
  input.disabled = state.busy;
}

function renderHeader() {
  picker.replaceChildren();
  if (!state.cases.length) {
    picker.append(el("option", { value: "" }, "No cases yet"));
  }
  state.cases.forEach((item) => {
    const option = el("option", { value: item.case_id }, `${item.title} · ${item.status}`);
    if (item.case_id === state.caseId) option.selected = true;
    picker.append(option);
  });
  picker.disabled = !state.cases.length;

  const current = state.cases.find((item) => item.case_id === state.caseId);
  contextLabel.textContent = current ? current.status : "Investment committee";
  recordLink.href = state.caseId ? `record.html?case=${state.caseId}` : "record.html";
  recordLink.style.visibility = state.caseId ? "visible" : "hidden";
}

function renderThread() {
  thread.replaceChildren();
  state.messages.forEach((message) => {
    if (message.role === "user") {
      thread.append(el("div", { class: "msg is-user" }, el("div", { class: "bubble" }, message.content)));
      return;
    }
    const block = el("div", { class: "msg is-yukti" });
    const body = el("div", { class: "reply" });
    if (typeof message.content === "string") {
      body.append(richText(message.content));
    } else {
      body.append(message.content);
    }
    if (message.recordSources && message.recordSources.length) {
      body.append(
        el(
          "p",
          { class: "provenance" },
          `read from the record: ${message.recordSources.join(", ")}`,
        ),
      );
    }
    block.append(body);
    thread.append(block);
  });
  if (state.busy) {
    thread.append(
      el("div", { class: "msg is-yukti" }, el("div", { class: "reply working" }, "Working…")),
    );
  }
  scrollDown();
}

function renderChips() {
  chips.replaceChildren();
  if (state.busy || state.pending) return;
  const prompts = (state.detail && state.detail.suggestions) || [];
  const extra = [];
  if (!state.cases.length) extra.push("Load the worked example");
  if (state.detail && state.detail.case && !state.detail.case.judgments.length) {
    if (state.detail.case.figures.length) extra.push("Run the analysis");
  }
  if (state.detail && state.detail.judgment && !state.detail.case.ledger.length) {
    extra.push("Record the decision");
  }
  [...extra, ...prompts].slice(0, 6).forEach((label) => {
    const chip = el("button", { class: "chip", type: "button" }, label);
    chip.addEventListener("click", () => submit(label));
    chips.append(chip);
  });
}

/* ------------------------------------------------------------- actions */

async function act(fn) {
  state.busy = true;
  render();
  try {
    await fn();
  } catch (error) {
    say("yukti", `That did not work: ${error.message}`);
  }
  state.busy = false;
  render();
}

async function refreshCases() {
  const payload = await api("GET", "/api/cases");
  state.cases = payload.cases;
}

async function loadCase(caseId) {
  state.detail = await api("GET", `/api/cases/${caseId}`);
  state.caseId = caseId;
}

async function loadWorkedExample() {
  await act(async () => {
    const detail = await api("POST", "/api/worked-example", {});
    await refreshCases();
    state.detail = detail;
    state.caseId = detail.case.case_id;
    say(
      "yukti",
      `Opened **${detail.title}** with the worked example's material already ` +
        `on file — ${detail.case.figures.length} figures across ${detail.case.sources.length} ` +
        "sources. Nothing has been analysed yet. Say **run the analysis** when you are ready.",
    );
  });
}

async function runAnalysis() {
  if (!state.caseId) return say("yukti", "Pick or open a case first.");
  await act(async () => {
    state.detail = await api("POST", `/api/cases/${state.caseId}/analysis`, {});
    await refreshCases();
    const judgment = state.detail.judgment;
    say("yukti", verdictCard(judgment), {});
  });
}

function verdictCard(judgment) {
  const card = el("div", { class: "verdict" });
  card.append(
    el("p", { class: "verdict-kicker" }, `${judgment.judgment_id} · ${judgment.recorded_on}`),
    el("h2", {}, judgment.recommendation),
    el("p", { class: "verdict-guidance" }, judgment.outcome_guidance),
  );
  const facts = el("div", { class: "verdict-facts" });
  facts.append(
    fact("Institutional confidence", judgment.confidence),
    fact("Conditions", String(judgment.conditions.length)),
    fact("Contested topics", String(judgment.disagreements.length)),
    fact("Material", judgment.snapshot_id || "—"),
  );
  card.append(facts);
  card.append(el("p", { class: "verdict-limit" }, `Limited by: ${judgment.confidence_note}`));
  const actions = el("div", { class: "card-actions" });
  ["Why this recommendation?", "What is limiting confidence?", "What are the conditions?"].forEach(
    (label) => {
      const button = el("button", { class: "chip", type: "button" }, label);
      button.addEventListener("click", () => submit(label));
      actions.append(button);
    },
  );
  card.append(actions);
  return card;
}

function fact(label, value) {
  return el("div", { class: "fact" }, el("span", { class: "fact-label" }, label), el("span", { class: "fact-value" }, value));
}

/* ------------------------------------------------------- prose intake */

async function readProse(text) {
  if (!state.caseId) {
    say("yukti", "Pick or open a case first — material has to land somewhere.");
    return;
  }
  await act(async () => {
    const payload = await api("POST", `/api/cases/${state.caseId}/read`, { text });
    if (payload.read_by && payload.read_by !== "model" && payload.read_by !== "reader") {
      say("yukti", `Note: ${payload.read_by}.`);
    }
    if (!payload.proposals.length) {
      say(
        "yukti",
        "I could not read any of the fifteen scheduled figures out of that. " +
          "I only recognise the schedule's own metrics, and I do not guess a " +
          "value to fill a gap. You can record figures directly on the full record.",
      );
      return;
    }
    say("yukti", proposalCard(payload));
  });
}

function proposalCard(payload) {
  const card = el("div", { class: "proposals" });
  card.append(
    el(
      "p",
      { class: "proposals-lead" },
      `I read ${payload.proposals.length} figure(s) out of that` +
        (payload.read_by === "model" ? " using the model" : "") +
        ". None of it is on file yet — accept what is right, fix what is not.",
    ),
  );

  // A figure may not cite a source that is not registered, so if the text
  // named no source I recognise and the case has none on file either, every
  // row below is stuck at "pick a source" with nothing to pick. Say so and
  // point at the one place a source can actually be added from scratch —
  // the full record's Material tab already has that control; chat does not
  // duplicate it here.
  const registeredSources = (state.detail && state.detail.case.sources) || [];
  if (!payload.sources.length && !registeredSources.length) {
    card.append(
      el(
        "p",
        { class: "proposals-gap" },
        "None of these can be accepted yet — no source was named in that text, " +
          "and this case has none on file either, so there is nothing to cite. ",
        el(
          "a",
          { href: `record.html?case=${state.caseId}`, target: "_blank", rel: "noopener" },
          "Register a source on the full record's Material tab",
        ),
        ", then come back and paste this again.",
      ),
    );
  }

  // Sources first: a figure may not cite a source that is not registered, so
  // confirming the documents the memo named is the step that unblocks the rest.
  const sourceControls = [];
  if (payload.sources.length) {
    const box = el("div", { class: "proposed-sources" });
    box.append(
      el(
        "p",
        { class: "proposed-sources-lead" },
        "Documents this text refers to. They are not in the register yet — " +
          "confirm the ones you actually hold.",
      ),
    );
    payload.sources.forEach((source) => {
      const keep = el("input", { type: "checkbox" });
      keep.checked = true;
      const kind = el("select", { class: "proposal-status" });
      (state.schedule ? state.schedule.source_kinds : []).forEach((option) => {
        const node = el("option", { value: option.key }, option.label);
        if (option.key === source.kind) node.selected = true;
        kind.append(node);
      });
      box.append(
        el(
          "label",
          { class: "proposed-source" },
          keep,
          el("span", { class: "proposed-source-label" }, source.label),
          el("span", { class: "proposed-source-origin" }, source.origin),
          kind,
        ),
      );
      sourceControls.push({ source, keep, kind });
    });
    card.append(box);
  }

  const rows = el("div", { class: "proposal-rows" });
  const controls = [];

  payload.proposals.forEach((proposal) => {
    const row = el("div", { class: "proposal" });
    const value = el("input", { type: "text", value: proposal.value, class: "proposal-value" });
    const status = el("select", { class: "proposal-status" });
    (state.schedule ? state.schedule.figure_statuses : []).forEach((option) => {
      const node = el("option", { value: option.key }, option.label);
      if (option.key === proposal.status) node.selected = true;
      status.append(node);
    });
    const source = el("select", { class: "proposal-source" });
    source.append(el("option", { value: "" }, "— pick a source —"));
    const available = [
      ...((state.detail && state.detail.case.sources) || []),
      ...payload.sources,
    ];
    available.forEach((item) => {
      const node = el("option", { value: item.label }, `${item.label} · ${item.origin}`);
      if (item.label === proposal.source_label) node.selected = true;
      source.append(node);
    });
    const keep = el("input", { type: "checkbox", class: "proposal-keep" });
    keep.checked = true;

    row.append(
      el("label", { class: "proposal-head" }, keep, el("span", { class: "proposal-label" }, proposal.label), el("span", { class: "proposal-unit" }, proposal.unit)),
      el("div", { class: "proposal-fields" }, value, status, source),
      el("p", { class: "proposal-quote" }, `“${proposal.span.quote}”`),
      el("p", { class: "proposal-basis" }, proposal.basis),
    );
    if (proposal.needs_attention) row.classList.add("needs-attention");
    rows.append(row);
    controls.push({ proposal, keep, value, status, source });
  });

  card.append(rows);

  if (payload.unmatched.length) {
    card.append(
      el(
        "p",
        { class: "proposals-gap" },
        `Not in that text: ${payload.unmatched.map((item) => item.label).join(", ")}. ` +
          "A blank is recorded as a gap and reported; it is never read as a zero.",
      ),
    );
  }

  const accept = el("button", { class: "primary", type: "button" }, "Accept the ticked figures");
  accept.addEventListener("click", async () => {
    const accepted = controls
      .filter((entry) => entry.keep.checked)
      .map((entry) => ({
        metric: entry.proposal.metric,
        value: entry.value.value.trim(),
        status: entry.status.value,
        source_label: entry.source.value,
        quote: entry.proposal.span.quote,
        basis: entry.proposal.basis,
        recorded_on: "",
        edited:
          entry.value.value.trim() !== entry.proposal.value ||
          entry.status.value !== entry.proposal.status ||
          entry.source.value !== entry.proposal.source_label,
      }));
    const sources = sourceControls
      .filter((entry) => entry.keep.checked)
      .map((entry) => ({
        label: entry.source.label,
        origin: entry.source.origin,
        kind: entry.kind.value,
      }));
    const registered = new Set([
      ...((state.detail && state.detail.case.sources) || []).map((item) => item.label),
      ...sources.map((item) => item.label),
    ]);
    const missing = accepted.filter((entry) => !registered.has(entry.source_label));
    if (!accepted.length && !sources.length) {
      say("yukti", "Nothing was ticked, so nothing was recorded.");
      return;
    }
    if (missing.length) {
      say(
        "yukti",
        "Every figure must cite a source in the register, and that is the one " +
          "rule here that exists purely for the audit trail. Unsourced, or " +
          `citing a source you unticked: ${missing.map((e) => e.metric).join(", ")}.`,
      );
      return;
    }
    accept.disabled = true;
    await act(async () => {
      state.detail = await api("POST", `/api/cases/${state.caseId}/accept`, {
        accepted,
        sources,
      });
      await refreshCases();
      const edits = accepted.filter((entry) => entry.edited).length;
      const outstanding = state.detail.outstanding.length;
      say(
        "yukti",
        (sources.length ? `Registered ${sources.length} source(s). ` : "") +
          `Recorded ${accepted.length} figure(s)${edits ? `, ${edits} of them corrected on the way in` : ""}. ` +
          (outstanding
            ? `${outstanding} still outstanding on the schedule.`
            : "The schedule is complete — say **run the analysis**."),
      );
    });
  });

  card.append(el("div", { class: "card-actions" }, accept));
  return card;
}

/* ----------------------------------------------------- guided flows */

function openCaseFlow() {
  // Required here matches what `cases.py::open_case` actually enforces —
  // company, stage, sector, owner and requested_decision. Only thesis is
  // optional server side. A field marked optional here that the server
  // rejects anyway is a dead end with no explanation, which is worse than
  // just asking for it up front.
  const fields = [
    ["company", "Company", true],
    ["stage", "Stage", true],
    ["sector", "Sector", true],
    ["owner", "Case owner", true],
    ["requested_decision", "What is being asked", true],
  ];
  const box = el("div", { class: "flow" });
  box.append(el("p", {}, "What is the committee being asked to decide?"));
  const inputs = {};
  fields.forEach(([name, label, required]) => {
    const node = el("input", { type: "text", placeholder: label });
    if (required) node.required = true;
    inputs[name] = node;
    box.append(el("label", { class: "flow-field" }, el("span", {}, label), node));
  });
  const go = el("button", { class: "primary", type: "button" }, "Open the case");
  go.addEventListener("click", async () => {
    const body = {};
    Object.entries(inputs).forEach(([name, node]) => (body[name] = node.value.trim()));
    body.thesis = "";
    const missing = fields
      .filter(([name, , required]) => required && !body[name])
      .map(([, label]) => label);
    if (missing.length) {
      say("yukti", `A case needs at least: ${missing.join(", ")}.`);
      return;
    }
    go.disabled = true;
    state.pending = null;
    // `act()` reports a failure as a chat message rather than throwing, so
    // the only way to know the request did not land is a flag the inner
    // function sets on its way out. Only a confirmed success leaves the
    // button disabled — a failure must always give it back.
    let opened = false;
    await act(async () => {
      const detail = await api("POST", "/api/cases", body);
      await refreshCases();
      state.detail = detail;
      state.caseId = detail.case.case_id;
      opened = true;
      say(
        "yukti",
        `Opened **${detail.title}**. Now paste whatever you have — a memo, ` +
          "notes, a paragraph from the deck — and I will read what I can out of it. " +
          "You will confirm every figure before it goes on file.",
      );
    });
    if (!opened) {
      go.disabled = false;
      state.pending = "intake";
    }
  });
  box.append(el("div", { class: "card-actions" }, go));
  state.pending = "intake";
  return box;
}

function decisionFlow() {
  const judgment = state.detail && state.detail.judgment;
  if (!judgment) {
    say("yukti", "There is no judgment to record a decision against yet.");
    return null;
  }
  const box = el("div", { class: "flow" });
  box.append(
    el(
      "p",
      {},
      `Recording against ${judgment.judgment_id} (${judgment.recommendation} at ` +
        `${judgment.confidence} confidence). The decision binds to this judgment permanently.`,
    ),
  );
  const decision = el("select", {});
  ["Approved", "Approved with conditions", "Deferred pending further diligence", "Declined"].forEach(
    (label) => decision.append(el("option", { value: label }, label)),
  );
  const by = el("input", { type: "text", placeholder: "Investment Committee" });
  const on = el("input", { type: "date", value: new Date().toISOString().slice(0, 10) });
  const why = el("textarea", { rows: "3", placeholder: "Rationale" });
  box.append(
    el("label", { class: "flow-field" }, el("span", {}, "Decision"), decision),
    el("label", { class: "flow-field" }, el("span", {}, "Decided by"), by),
    el("label", { class: "flow-field" }, el("span", {}, "Recorded on"), on),
    el("label", { class: "flow-field" }, el("span", {}, "Rationale"), why),
  );
  const go = el("button", { class: "primary", type: "button" }, "Record it");
  go.addEventListener("click", async () => {
    go.disabled = true;
    state.pending = null;
    // Same failure-recovery shape as `openCaseFlow`: only a confirmed
    // success leaves the button disabled.
    let recorded = false;
    await act(async () => {
      state.detail = await api("POST", `/api/cases/${state.caseId}/decision`, {
        decision: decision.value,
        decided_by: by.value.trim() || "Investment Committee",
        recorded_on: on.value,
        rationale: why.value.trim(),
      });
      await refreshCases();
      recorded = true;
      say(
        "yukti",
        `Recorded: **${decision.value}**, bound to ${judgment.judgment_id}. ` +
          "It stays bound there — re-analysing creates a new judgment and never " +
          "reaches back into a decision already taken.",
      );
    });
    if (!recorded) {
      go.disabled = false;
      state.pending = "decision";
    }
  });
  box.append(el("div", { class: "card-actions" }, go));
  state.pending = "decision";
  return box;
}

/* --------------------------------------------------------- dispatch */

const RUN = /\b(run|analyse|analyze|request)\b.*\b(analysis|judgment|judgement|it)\b|^run it$|^analyse$|^analyze$/i;
const OPEN = /\b(open|start|create|new)\b.*\bcase\b/i;
const DECIDE = /\b(record|make|enter)\b.*\bdecision\b|^decide$/i;
const EXAMPLE = /worked example|load the example|demo case/i;

/* Prose, as opposed to a question: long, and carrying at least one number.
   A question about the record is short and rarely has a figure in it. */
function looksLikeMaterial(text) {
  return text.length >= 80 && /\d/.test(text);
}

async function submit(raw) {
  const text = raw.trim();
  if (!text || state.busy) return;
  say("user", text);
  input.value = "";
  autoGrow();

  if (EXAMPLE.test(text)) return loadWorkedExample();
  if (OPEN.test(text)) return say("yukti", openCaseFlow());
  if (DECIDE.test(text)) {
    const flow = decisionFlow();
    if (flow) say("yukti", flow);
    return;
  }
  if (RUN.test(text)) return runAnalysis();
  if (looksLikeMaterial(text)) return readProse(text);

  if (!state.caseId) {
    return say(
      "yukti",
      "No case is open. Say **open a case**, or **load the worked example** to " +
        "see the whole thing run on real material.",
    );
  }

  await act(async () => {
    const payload = await api("POST", `/api/cases/${state.caseId}/ask`, { question: text });
    // Say which path answered. A phrased answer is the record's answer in the
    // model's words; a "record" answer is the record's own words. The reader
    // should never have to guess which one they are reading.
    const from = [];
    if (payload.understood) from.push(...payload.record_sources);
    if (payload.phrased_by === "model") from.push("phrased by the model");
    if (payload.note) from.push(payload.note);
    say("yukti", payload.answer, { recordSources: from });
  });
}

/* ------------------------------------------------------------- boot */

function autoGrow() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 200)}px`;
}

function greet() {
  const lines = [
    "I carry an investment case from messy notes to a decision the committee can defend.",
    "",
    "Paste whatever you have and I will read the diligence figures out of it — " +
      "you confirm each one before it goes on file. Then I run the reasoning engine " +
      "over the material and answer questions from what it recorded, not from " +
      "anything I make up.",
  ];
  say("yukti", lines.join("\n"));
  if (!state.cases.length) {
    say(
      "yukti",
      "Nothing is on file yet. Say **load the worked example** to walk the whole " +
        "lifecycle on real material, or **open a case** to start your own.",
    );
  }
}

async function boot() {
  try {
    state.schedule = await api("GET", "/api/schedule");
    await refreshCases();
    const wanted = new URLSearchParams(location.search).get("case");
    const first = wanted || (state.cases[0] && state.cases[0].case_id);
    if (first) await loadCase(first);
  } catch (error) {
    say("yukti", `Could not reach the workspace: ${error.message}`);
  }
  state.booting = false;
  greet();
  render();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submit(input.value);
});

input.addEventListener("input", autoGrow);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    submit(input.value);
  }
});

picker.addEventListener("change", () => {
  const caseId = picker.value;
  if (!caseId) return;
  act(async () => {
    await loadCase(caseId);
    const record = state.detail.case;
    say(
      "yukti",
      `Switched to **${state.detail.title}** — ${state.detail.status.toLowerCase()}, ` +
        `${record.figures.length} of 15 figures recorded.`,
    );
  });
});

boot();
