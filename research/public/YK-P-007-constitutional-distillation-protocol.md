# Constitutional Distillation Protocol

| | |
|---|---|
| **Document ID** | YK-P-007 |
| **Source** | `choir/research/R007_Constitutional_Distillation_Protocol.md` (R007) |
| **Series** | CHOIR Research Proposals |
| **Revision** | Draft |
| **Status** | Open |
| **Last Updated** | 2026-08-23 |

> **Status note.** This document is **Open**: it is a proposal and not an accepted finding.
> The source is labelled `Status: Research Proposal` and `Version: R007 (Draft)`. Nothing in it
> has been accepted as specification, and the source reports no experiment, dataset, or
> measurement. Its central claims are recorded as hypotheses (§ Research Hypotheses).

> **Citation convention.** The source document does not number its sections. Inline references
> below therefore cite the source's own headings, in the form (§ Heading), so that any claim can
> be checked against the original.

## Abstract

The Constitutional Distillation Protocol (CDP) is proposed as a CHOIR primitive for converting
explicit institutional governance into implicit specialist behavior, so that specialist kernels
behave as though constitutional rules are permanently present rather than receiving those rules
as a prompt on every inference (§ Abstract). The proposal extends prompt distillation from
task-specific rule compression into what the source calls institutional reasoning preservation,
with the stated result that "governance becomes part of model behavior rather than runtime prompt
overhead" (§ Abstract). It is a research proposal: it defines a five-stage protocol, a two-layer
architecture, three hypotheses, four CHOIR-specific evaluation metrics, and three limitations, and
it reports no results against any of them.

## Research Question

The source states its problem directly. Modern AI systems repeatedly consume large system prompts
containing review policies, safety constraints, reasoning guidelines, formatting requirements,
escalation rules, and organizational standards; these "are expensive to transmit, difficult to
maintain, and easy to diverge across agents" (§ Problem Statement). The framing claim is set out
as a block quotation in the source:

> Organizations lose reasoning consistency when governance exists only as text instead of learned
> behavior.

The question the document sets out to answer follows from this: CHOIR "requires a mechanism that
preserves institutional reasoning across every cognitive kernel without duplicating constitutional
instructions every inference" (§ Problem Statement). The governing principle proposed as the answer
is stated as: "Governance should be internalized, not repeatedly instructed" (§ Core Principle).

The source draws the contrast against a narrow task example rather than against prompt distillation
as a field. Under the heading "Instead of distilling:" it quotes "Classify language."; under "We
distill:" it quotes "Reason like this institution." (§ Core Principle).

## Finding

The document's conclusion is a proposed protocol, not an empirical result. What it establishes is a
specification of that protocol together with an explicit account of what would have to be true for
it to work and what remains untested.

### The five-stage protocol

CDP is defined in five stages (§ Constitutional Distillation Protocol).

| Stage | Name | What the source specifies |
|---|---|---|
| 1 | Constitution Definition | The institution defines its constitutional rules — evidence standards, acceptable uncertainty, escalation policies, precedent handling, disagreement protocols, formatting conventions. These become the constitutional prompt. |
| 2 | Teacher Deliberation | A teacher model operates under the full constitution over real organizational decisions and produces constitutionally compliant reasoning. |
| 3 | Distillation Dataset | Runtime prompts are stripped away; the student receives an institutional case as input and teacher-produced reasoning as target. |
| 4 | Specialist Kernel Formation | Role-specific kernels are created rather than a single distilled model. |
| 5 | Runtime Execution | No constitutional prompt is injected; the scheduler decides only role, effort, and rounds. |

Stage 1 carries an explicit constraint on the constitutional prompt: it "is **not** intended for
long-term runtime use. Its purpose is to teach" (§ Stage 1 — Constitution Definition).

Stage 2 names the inputs as real organizational decisions — investment memos, QA incidents,
architecture reviews, customer escalations, committee discussions — and the teacher's output as
conclusions, structured reasoning, citations, uncertainty, objections, and resolutions. The teacher
"becomes the institutional exemplar" (§ Stage 2 — Teacher Deliberation).

Stage 3 states that "The student never receives the constitutional prompt directly. Instead, it
learns behaviors demonstrated by the teacher." The source states this "mirrors the prompt
distillation workflow demonstrated in Tinker" (§ Stage 3 — Distillation Dataset). The source
presents the five stages as a flat sequence and does not rank any one of them above the others.

Stage 4 gives a role table, presented in the source as an example rather than a fixed roster
(§ Stage 4 — Specialist Kernel Formation):

| Kernel | Distilled behavior |
|---|---|
| Historian | precedent-first |
| Librarian | evidence discipline |
| Contrarian | assumption challenge |
| First Principles | decomposition |
| Expansionist | alternative generation |

The stated invariant is that "Every kernel shares the same constitutional foundation while expressing
different reasoning roles" (§ Stage 4 — Specialist Kernel Formation).

Stage 5 states the runtime consequence: the constitutional behavior "already exists inside the
kernel", so the scheduler's remaining decisions are role, effort, and rounds only
(§ Stage 5 — Runtime Execution).

### Two-layer architecture

The source separates a Constitutional Layer from a Runtime Layer (§ Architectural Model —
Two-Layer System). Layer 1 holds governance, precedent, institutional philosophy, reasoning
standards, and escalation policies; the source's characterisation is one sentence: "This layer
teaches." Layer 2 contains the Historian, Contrarian, First Principles, Expansionist, and Librarian
kernels, which "execute decisions without repeatedly loading constitutional instructions."

### Claimed benefits, as stated

The source gives three (§ Why This Matters).

1. **Reduced Prompt Overhead.** Long constitutional prompts disappear from runtime; inference becomes
   cheaper, latency decreases, context remains cleaner. The source ties this to "the efficiency
   motivation behind prompt distillation" rather than to any measurement of its own.
2. **Consistent Institutional Behavior.** Every kernel inherits the same governance, so that CHOIR is
   composed of "Five constitutionally aligned specialists" rather than "Five differently prompted
   agents."
3. **Organizational DNA.** The source introduces this as a new concept: "The constitutional behavior
   of an institution becomes a trainable artifact", with investment philosophy, engineering culture,
   QA methodology, and legal reasoning style given as examples. The distinction drawn is that
   "Rather than preserving documents— CHOIR preserves demonstrated reasoning."

These are asserted, not demonstrated. No cost, latency, or consistency figure appears anywhere in the
source document.

### Relationship to the Deliberation Cohort

The source is explicit that CDP "complements—not replaces—the Deliberation Cohort"
(§ Relationship to Deliberation Cohorts), and tabulates the division:

| Cohort Component | CDP Contribution |
|---|---|
| Role | preserved |
| Effort | preserved |
| Rounds | preserved |
| Governance | internalized |

The stated effect is that "Every cohort member begins with constitutional alignment before
deliberation starts."

### Hypotheses, not results

The three claims are recorded as hypotheses (§ Research Hypotheses), verbatim:

- **H1** — Distilled constitutional behavior reduces prompt tokens while preserving institutional
  consistency.
- **H2** — Role-specific constitutional distillation produces stronger specialization than a single
  universal distilled model.
- **H3** — Institutions transfer culture more effectively through demonstrated decisions than through
  static policy documents.

None of H1, H2, or H3 is tested in the source document. No training run, baseline, or comparison is
reported.

### Evaluation metrics — named, not operationalized

Alongside accuracy, latency, and token cost, the source names four CHOIR-specific metrics
(§ Evaluation Metrics): **Constitutional Fidelity** (how closely runtime behavior matches teacher
behavior), **Precedent Compliance** (whether reasoning correctly applies historical decisions),
**Dissent Quality** (whether objections improve institutional decisions), and **Governance
Consistency** (whether different kernels apply the same constitutional principles). Each is given a
one-line definition. The source supplies no measurement procedure, scoring scale, threshold, or
baseline for any of them.

### Limitations recorded by the source

The source states that "Prompt distillation inherits important constraints" and records three
(§ Limitations):

- **Demonstration Dependence.** "A student can only learn behaviors the teacher actually
  demonstrates." The implication the source itself draws: "Organizations cannot preserve reasoning
  they have never exhibited."
- **Coverage Risk.** "Rare constitutional edge cases require representative examples."
- **Constitutional Drift.** "Institutions evolve. Distilled kernels require periodic constitutional
  refresh cycles."

### Citation status

The source's appeals to prior work on prompt distillation are carried by unresolved citation
placeholders — `<Cite refs={["turn0search0","turn0search1"]}/>` and `<Cite ref=turn0search0/>` —
appearing in § Core Principle, § Stage 3 — Distillation Dataset, § Why This Matters (1. Reduced
Prompt Overhead), and § Limitations (Demonstration Dependence). The only named prior system is
"Tinker" (§ Stage 3 — Distillation Dataset). The document contains no bibliography or reference
list, so these citations cannot be resolved from the document as it stands.

### Canonical axiom

The document closes with a stated axiom (§ Canonical Axiom):

> Governance should not live in prompts.
>
> Governance should live in behavior.

and with the summary claim that "institutional reasoning becomes durable only when governance is
transformed from explicit instructions into internalized cognitive behavior shared across every
specialist kernel within CHOIR" (§ Canonical Axiom). Note the modality: the source frames this as
what the protocol *proposes*, not as an established result.

## Architectural Implications

Only implications the source itself draws are listed here.

- **CHOIR gains a two-layer split.** Governance moves out of the runtime path into a separate
  Constitutional Layer whose function is to teach; the Runtime Layer holds the five named kernels
  and executes without loading constitutional instructions (§ Architectural Model — Two-Layer
  System).
- **The runtime scheduler's responsibility narrows.** Under CDP the scheduler decides only role,
  effort, and rounds, because constitutional behavior is already resident in the kernel
  (§ Stage 5 — Runtime Execution).
- **The Deliberation Cohort's interface is unchanged.** Role, effort, and rounds are all preserved;
  only governance changes status, from injected to internalized (§ Relationship to Deliberation
  Cohorts).
- **Kernels multiply rather than consolidate.** CHOIR creates role-specific kernels — Historian,
  Librarian, Contrarian, First Principles, Expansionist — instead of one distilled model
  (§ Stage 4 — Specialist Kernel Formation).
- **Distilled kernels require periodic constitutional refresh.** Because institutions
  evolve, distilled kernels "require periodic constitutional refresh cycles"
  (§ Limitations — Constitutional Drift), and constitutional versioning is listed as future work
  (§ Future Research). CHOIR would therefore have to carry a refresh mechanism, which the source
  does not specify.
- **The institution's decision history becomes a training input.** Real organizational decisions —
  investment memos, QA incidents, architecture reviews, customer escalations, committee discussions —
  are the corpus the teacher operates over (§ Stage 2 — Teacher Deliberation), which means CHOIR's
  behavior is bounded by what the institution has actually exhibited
  (§ Limitations — Demonstration Dependence).

The source names DAALE (Data Algorithmically Analytical Logical Engine) as the engine in its header
block, but draws no implication for DAALE anywhere in the body. Any consequence for DAALE is
not stated in the source document.

## Open Questions

Recorded by the source as future work (§ Future Research):

- constitutional versioning
- automatic constitution extraction from decision history
- on-policy constitutional reinforcement
- disagreement-aware constitutional updates
- cross-organization constitutional transfer

Further gaps and untested items the source records or leaves open:

- **H1, H2, and H3 are untested.** The source states them as hypotheses and reports no experiment,
  dataset, model, or measurement against any of them (§ Research Hypotheses).
- **The four CHOIR-specific metrics are undefined operationally.** Constitutional Fidelity, Precedent
  Compliance, Dissent Quality, and Governance Consistency each have a one-line description and no
  measurement procedure or threshold (§ Evaluation Metrics).
- **Coverage of rare constitutional edge cases is unresolved.** The source states such cases "require
  representative examples" but does not say how such examples are to be identified or produced
  (§ Limitations — Coverage Risk).
- **The refresh cadence for constitutional drift is unspecified.** "Periodic" is the only
  qualification given (§ Limitations — Constitutional Drift).
- **The prior work is uncited in resolvable form.** The claims about prompt distillation rest on
  placeholder citation tokens and a single product name, "Tinker", with no reference list in the
  document (§ Core Principle, § Stage 3 — Distillation Dataset, § Why This Matters, § Limitations).
- **The efficiency claims are unquantified.** "Inference becomes cheaper. Latency decreases."
  carry no figures, baselines, or conditions (§ Why This Matters — 1. Reduced Prompt Overhead).

## Related Documents

The source document cites no sibling YUKTI publication by identifier, and contains no reference list.
The following are named in the source but not cited by it:

- `YK-D-005-canonical-definition-of-daale.md` — YK-D-005, Canonical Definition of DAALE. The source
  names DAALE as its engine in the header block only. This ruling is **Superseded** and no longer
  governs; the source does not reference it.
- **Deliberation Cohort** — the source devotes a section to its relationship with the Deliberation
  Cohort (§ Relationship to Deliberation Cohorts), but no publication for the Deliberation Cohort
  appears in the publication index, so no link can be given.

No other sibling document is depended on, fed, or cited by the source.
