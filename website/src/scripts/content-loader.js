/*
  YUKTI Website — Content Loader (Build Order Step 2; Addendum v1.2)
  Populates DOM placeholders from homepage.content.js. One render function
  per scene, single responsibility, no templating engine (D1).
*/

import {
  homepageContent,
  primaryNav,
  pullQuote,
  footerContent,
  marginNotes,
  marginNoteUpdatedDate,
} from '../content/homepage.content.js';

/* ---------- shared helpers (Addendum v1.2) ---------- */

// Mega scene-heading: one word per line, each independently [data-reveal]
// inside the container's [data-reveal-group] (already set in markup).
function renderMegaHeading(el, text) {
  el.classList.add('yukti-heading-mega');
  el.innerHTML = text
    .split(' ')
    .map((word) => `<span class="yukti-mega-line" data-reveal>${word}</span>`)
    .join('');
}

// Living margin note — wide-viewport-only per-scene metadata block.
function renderMarginNote(sceneId) {
  const el = document.querySelector(`#${sceneId} .yukti-margin-note`);
  const note = marginNotes[sceneId];
  if (!el || !note) return;
  el.innerHTML = `
    <div class="yukti-margin-note__row"><b>Section</b>${note.section}</div>
    <div class="yukti-margin-note__row"><b>${note.name}</b></div>
    <div class="yukti-margin-note__row"><b>Drawing</b>${note.drawing}</div>
    <div class="yukti-margin-note__row"><b>Rev</b>${note.rev}</div>
    <div class="yukti-margin-note__row"><b>Sheet</b>${note.sheet}</div>
    <div class="yukti-margin-note__row"><b>Updated</b>${marginNoteUpdatedDate}</div>
  `;
}

/* ---------- nav ---------- */

function renderNav() {
  const list = document.getElementById('nav-links');
  if (!list) return;
  list.innerHTML = primaryNav
    .map((item) => `<li><a href="${item.href}">${item.label}</a></li>`)
    .join('');
}

/* ---------- hero (Addendum v1.2 — sparser composition, copy unchanged) ---------- */

function renderHero() {
  const { hero } = homepageContent;
  document.getElementById('hero-headline').textContent = hero.headline;

  // Supporting line as annotation text
  document.getElementById('hero-supporting').textContent = hero.supporting;

  const link = document.getElementById('hero-link');
  link.textContent = hero.link.label;
  link.setAttribute('href', hero.link.href);
}

/* ---------- why reasoning matters ---------- */

function renderWhyReasoningMatters() {
  const { whyReasoningMatters } = homepageContent;
  document.getElementById('wrm-index').textContent = marginNotes['why-reasoning-matters'].section;
  renderMegaHeading(document.getElementById('wrm-heading'), whyReasoningMatters.heading);
  const body = document.getElementById('wrm-body');
  body.innerHTML = whyReasoningMatters.body
    .map((p) => `<p class="yukti-type-body" data-reveal>${p}</p>`)
    .join('');
  renderMarginNote('why-reasoning-matters');
}

/* ---------- approach ---------- */

function renderApproach() {
  const { approach } = homepageContent;
  document.getElementById('approach-index').textContent = marginNotes.approach.section;
  renderMegaHeading(document.getElementById('approach-heading'), approach.heading);
  const list = document.getElementById('approach-principles');
  list.innerHTML = approach.principles.map((p) => `<li data-reveal>${p}</li>`).join('');
  renderMarginNote('approach');
}

/* ---------- evidence (Addendum v1.2 — pipeline diagram) ---------- */

function renderEvidence() {
  const { evidence } = homepageContent;
  document.getElementById('evidence-index').textContent = marginNotes.evidence.section;
  renderMegaHeading(document.getElementById('evidence-heading'), evidence.heading);

  const { claim, evidenceNodes, result } = evidence.trace;

  const stage = ({ label, value }, extraClass = '') => `
    <div class="yukti-pipeline__stage${extraClass ? ` ${extraClass}` : ''}">
      <span class="yukti-pipeline__label">${label}</span>
      <p class="yukti-pipeline__value">${value}</p>
    </div>`;

  const pipeline = document.getElementById('evidence-trace');
  pipeline.innerHTML = `
    <div class="yukti-pipeline__claim" data-reveal>
      <span class="yukti-pipeline__label">Claim</span>
      <p class="yukti-pipeline__value">${claim.value}</p>
    </div>
    <div class="yukti-pipeline__stages" data-reveal>
      ${stage(evidenceNodes[0])}
      ${stage(evidenceNodes[1])}
      ${stage(result, 'is-result')}
    </div>
    <div class="yukti-pipeline__annotation yukti-material-paper" data-reveal>
      <span class="yukti-pipeline__label">Annotation</span>
      <p class="yukti-pipeline__value">${evidence.closing}</p>
    </div>
  `;
  renderMarginNote('evidence');
}

/* ---------- pull quote (Addendum v1.2, new scene) ---------- */

function renderPullQuote() {
  const el = document.getElementById('pull-quote-text');
  if (!el) return;
  el.innerHTML = pullQuote.lines
    .map((line, i) => `<span style="--stagger: ${i * 150}ms" data-reveal>${line}</span>`)
    .join('');
}

/* ---------- applications (Addendum v1.2 — stacked sequence) ---------- */

function renderApplications() {
  const { applications } = homepageContent;
  document.getElementById('applications-index').textContent = marginNotes.applications.section;
  renderMegaHeading(document.getElementById('applications-heading'), applications.heading);

  const list = document.getElementById('applications-domains');
  list.innerHTML = applications.domains
    .map(
      ({ name, statement }, i) => `
      ${i > 0 ? '<hr class="yukti-rule--tick yukti-app-divider" />' : ''}
      <div class="yukti-app-entry" data-reveal>
        <h3 class="yukti-app-entry__name">${name}</h3>
        <p class="yukti-app-entry__copy">${statement}</p>
      </div>`
    )
    .join('');
  renderMarginNote('applications');
}

/* ---------- philosophy (Addendum v1.2 — fullscreen scroll-snap) ---------- */

function renderPhilosophy() {
  const { philosophy } = homepageContent;
  document.getElementById('philosophy-index').textContent = marginNotes.philosophy.section;
  renderMegaHeading(document.getElementById('philosophy-heading'), philosophy.heading);

  const statements = document.getElementById('philosophy-statements');
  statements.innerHTML = philosophy.commitments
    .map((commitment) => {
      const [first, second] = commitment.split(' over ');
      return `
        <div class="yukti-philosophy__statement" data-reveal>
          <p class="yukti-philosophy__word">${first}</p>
          <p class="yukti-philosophy__over">over</p>
          <p class="yukti-philosophy__word">${second}</p>
        </div>`;
    })
    .join('');
  renderMarginNote('philosophy');
}

/* ---------- contact — UNCHANGED ---------- */

function renderContact() {
  const { contact } = homepageContent;
  document.getElementById('contact-heading').textContent = contact.heading;
  document.getElementById('contact-statement').textContent = contact.statement;
  const links = document.getElementById('contact-links');
  links.innerHTML = contact.links
    .map(
      ({ name, role, url }) => `
      <a class="yukti-quiet-link" href="${url}" target="_blank" rel="noopener noreferrer">
        ${name.toUpperCase()} &mdash; ${role}
      </a>`
    )
    .join('');
  document.getElementById('contact-location').textContent = contact.location;
}

/* ---------- footer (Addendum v1.2 — blueprint sign-off) ---------- */

function renderFooter() {
  document.getElementById('footer-tagline').textContent = footerContent.tagline;
  document.getElementById('footer-revision').textContent = footerContent.revision;
  document.getElementById('footer-prepared').textContent = footerContent.prepared;
}

/* ---------- init ---------- */

renderNav();
renderHero();
renderWhyReasoningMatters();
renderApproach();
renderEvidence();
renderPullQuote();
renderApplications();
renderPhilosophy();
renderContact();
renderFooter();