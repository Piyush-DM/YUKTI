/*
  YUKTI Homepage Content — v1 MOCK COPY
  Source: YUKTI_Website_Mock_Copywriting_v1.docx (supplied 2026-07-29)
  Status: placeholder copy, written in the correct voice/structure — NOT final
  (the source document itself states this pending final editorial review).

  This file is the single source of truth for homepage copy. Swapping to final
  copy during editorial review should mean editing values here only — no
  component, layout, or motion code should need to change (content/markup
  separation, architecture D3). See CONTENT_VOICE_GUIDE.md for the voice rules
  any replacement copy must also satisfy.
*/

export const homepageContent = {
  hero: {
    id: 'hero',
    headline: 'Institutional reasoning, grounded in evidence.',
    supporting:
      'Every conclusion should remain connected to the evidence that produced it. ' +
      'YUKTI is building reasoning systems where assumptions, findings, claims, and ' +
      'decisions can be inspected instead of accepted on faith.',
    link: { label: 'Explore the reasoning.', href: '#why-reasoning-matters' },
  },

  whyReasoningMatters: {
    id: 'why-reasoning-matters',
    heading: 'Why Reasoning Matters',
    body: [
      'Modern AI systems are exceptionally good at producing answers. Institutions, ' +
        'however, are rarely judged by answers alone. They are judged by whether those ' +
        'answers can be justified, audited, challenged, and defended months or years later.',
      'Confidence is persuasive. Reasoning is accountable. YUKTI focuses on the latter.',
    ],
  },

  approach: {
    id: 'approach',
    heading: 'How YUKTI Approaches Problems',
    principles: [
      'Every conclusion should remain connected to evidence.',
      'Every assumption should be visible.',
      'Every change should produce an explainable difference.',
      'Every recommendation should survive scrutiny.',
    ],
  },

  evidence: {
    id: 'evidence',
    heading: 'Evidence',
    // Confirmed shape (see turn note): a linear 3-node trace, not a multi-source
    // graph. Feeds EvidenceTraceVisualization in Build Order Step 6.
    trace: {
      claim: { label: 'Example claim', value: '"Proceed with additional diligence."' },
      evidenceNodes: [
        { label: 'Supporting evidence', value: 'Infrastructure costs projected to decrease.' },
        { label: 'Updated finding', value: 'Updated operational finding weakens that assumption.' },
      ],
      result: { label: 'Result', value: '"Hold for review."' },
    },
    closing:
      'The important outcome is not that the recommendation changed — but that every ' +
      'step leading to that change can be inspected.',
  },

  applications: {
    id: 'applications',
    heading: 'Institutional Applications',
    // Rendered as DomainStatement, never DomainCard — see component tree's
    // explicit non-components list (no FeatureCard/FeatureGrid on this scene).
    domains: [
      { name: 'Investment', statement: 'Understand why an investment recommendation changed.' },
      { name: 'Insurance', statement: 'Trace underwriting decisions back to policy evidence.' },
      { name: 'Compliance', statement: 'Maintain defensible reasoning across changing regulations.' },
      { name: 'Procurement', statement: 'Document how vendor decisions were reached.' },
      { name: 'Research', statement: 'Preserve reasoning as evidence evolves over time.' },
    ],
  },

  philosophy: {
    id: 'philosophy',
    heading: 'Philosophy',
    commitments: [
      'Evidence over confidence.',
      'Transparency over opacity.',
      'Reasoning over prediction.',
      'Trust over persuasion.',
    ],
  },

  contact: {
    id: 'contact',
    heading: 'Contact',
    statement:
      "If your organization depends on decisions that must withstand scrutiny, we'd be happy to start a conversation.",
    email: 'contact@yukti.agency',
    location: 'Chandigarh, India',
  },
};

// Addendum v1.2 — authored directly by the user in the "YUKTI v3 —
// Architectural Editorial Design" brief, not placeholder. Used exactly once,
// as the homepage's single oversized-quotation moment (between Evidence and
// Applications).
export const pullQuote = {
  id: 'pull-quote',
  lines: ['Reasoning survives scrutiny.', "Confidence doesn't."],
};

// Addendum v1.2 — footer "blueprint sign-off." Tagline authored directly by
// the user in the v3 brief.
export const footerContent = {
  tagline: 'Institutional Reasoning Infrastructure',
  revision: '0.2',
  prepared: '2026',
};

// Addendum v1.2 — "living margin" per-scene metadata. Sheet total is the
// count of numbered scenes (01–05; Hero and Contact are not numbered, see
// architecture §15.3/§16). Drawing IDs are sequential, not derived from
// anything — purely a drafting-motif detail, not functional data.
export const marginNotes = {
  'why-reasoning-matters': { section: '01', name: 'Reasoning', drawing: 'YK-001', rev: 'A', sheet: '1/5' },
  approach: { section: '02', name: 'Approach', drawing: 'YK-002', rev: 'A', sheet: '2/5' },
  evidence: { section: '03', name: 'Evidence', drawing: 'YK-003', rev: 'A', sheet: '3/5' },
  applications: { section: '04', name: 'Applications', drawing: 'YK-004', rev: 'A', sheet: '4/5' },
  philosophy: { section: '05', name: 'Philosophy', drawing: 'YK-005', rev: 'A', sheet: '5/5' },
};
export const marginNoteUpdatedDate = '29 JUL 2026';

export const primaryNav = [
  { label: 'Reasoning', href: '#why-reasoning-matters' },
  { label: 'Approach', href: '#approach' },
  { label: 'Evidence', href: '#evidence' },
  { label: 'Applications', href: '#applications' },
  { label: 'Philosophy', href: '#philosophy' },
  { label: 'Contact', href: '#contact' },
];
