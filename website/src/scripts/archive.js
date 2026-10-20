const archiveNav = [
  { label: 'Home', href: '/' },
  { label: 'Documents', href: '/documents.html' },
  { label: 'Contact', href: '/#contact' },
];

const reservedDocuments = [
  ['R001', 'Institutional Arbitration'],
  ['R002', 'Proposal Structure'],
  ['R003', 'Evidence Representation'],
  ['R004', 'Uncertainty Representation'],
  ['R005', 'Contradiction Lifecycle'],
  ['R006', 'Traceability'],
];

const marginNote = {
  section: '06',
  name: 'Documents',
  drawing: 'YK-006',
  rev: 'A',
  sheet: '1/1',
  updated: '24 AUG 2026',
};

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&', '<': '<', '>': '>', '"': '"', "'": '&#039;',
  }[char]));
}

function renderNav() {
  const list = document.getElementById('nav-links');
  if (!list) return;
  list.innerHTML = archiveNav
    .map((item) => `<li><a href="${item.href}">${item.label}</a></li>`)
    .join('');
}

function renderMarginNotes() {
  document.querySelectorAll('[data-margin-note]').forEach((element) => {
    element.innerHTML = `
      <div class="yukti-margin-note__row"><b>Section</b>${marginNote.section}</div>
      <div class="yukti-margin-note__row"><b>${marginNote.name}</b></div>
      <div class="yukti-margin-note__row"><b>Drawing</b>${marginNote.drawing}</div>
      <div class="yukti-margin-note__row"><b>Rev</b>${marginNote.rev}</div>
      <div class="yukti-margin-note__row"><b>Sheet</b>${marginNote.sheet}</div>
      <div class="yukti-margin-note__row"><b>Updated</b>${marginNote.updated}</div>
    `;
  });
}

function statusClass(status) {
  return `yukti-status--${status.toLowerCase().replace(/\s+/g, '-')}`;
}

function renderRow(document) {
  return `
    <a class="yukti-archive__row" href="/document.html?id=${encodeURIComponent(document.id)}">
      <div class="yukti-archive__ident">
        <span class="yukti-archive__id">${escapeHtml(document.id)}</span>
        <span class="yukti-archive__rev">REV ${escapeHtml(document.revision)}</span>
      </div>
      <div class="yukti-archive__body">
        <h3 class="yukti-archive__title">${escapeHtml(document.title)}</h3>
        <p class="yukti-archive__abstract">${escapeHtml(document.abstract)}</p>
        <div class="yukti-archive__meta">
          <span class="yukti-status ${statusClass(document.status)}">${escapeHtml(document.status)}</span>
          <span>UPDATED ${escapeHtml(document.lastUpdated)}</span>
          <span>${escapeHtml(document.sections)} SECTIONS</span>
        </div>
      </div>
    </a>
  `;
}

function renderRegister(documents) {
  const root = document.getElementById('archive-register');
  const series = new Map();
  documents.forEach((item) => {
    if (!series.has(item.series)) series.set(item.series, []);
    series.get(item.series).push(item);
  });

  root.innerHTML = [...series]
    .map(([name, entries]) => `
      <section class="yukti-archive__series" aria-labelledby="series-${name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}">
        <div class="yukti-archive__series-head">
          <h2 id="series-${name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}" class="yukti-archive__series-name">${escapeHtml(name)}</h2>
          <span class="yukti-archive__series-count">${String(entries.length).padStart(2, '0')} SHEETS</span>
        </div>
        <div>${entries.map(renderRow).join('')}</div>
      </section>
    `)
    .join('');
}

function renderReserved() {
  const root = document.getElementById('archive-reserved');
  root.innerHTML = reservedDocuments
    .map(([id, title]) => `<div class="yukti-archive__reserved-row"><b>${escapeHtml(id)}</b><span>${escapeHtml(title)}</span></div>`)
    .join('');
}

function renderSkeleton() {
  const root = document.getElementById('archive-register');
  root.innerHTML = `
    <div class="yukti-archive__skeleton" aria-hidden="true" aria-label="Loading document register">
      ${Array.from({ length: 6 }, () => `
        <div class="skeleton-row">
          <div class="skeleton-line" style="width: 60%; height: 1rem;"></div>
          <div>
            <div class="skeleton-line" style="width: 40%;"></div>
            <div class="skeleton-line" style="width: 80%;"></div>
            <div class="skeleton-line" style="width: 60%;"></div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function emptyState() {
  const root = document.getElementById('archive-register');
  root.innerHTML = `
    <div class="yukti-shell yukti-archive__empty">
      <h2>No documents found</h2>
      <p>The archive is currently empty. Check back later.</p>
    </div>
  `;
}

function errorState(message) {
  const root = document.getElementById('archive-register');
  root.innerHTML = `
    <div class="yukti-shell yukti-archive__empty">
      <h2>Unable to load register</h2>
      <p>${escapeHtml(message)}</p>
      <a class="yukti-quiet-link" href="#" onclick="window.location.reload()">Try again</a>
    </div>
  `;
}

async function init() {
  renderNav();
  renderMarginNotes();
  renderReserved();
  document.getElementById('archive-heading').className = 'yukti-heading-mega';
  document.getElementById('archive-heading').innerHTML = '<span class="yukti-mega-line" data-reveal>DOCUMENTS</span>';

  renderSkeleton();

  try {
    const response = await fetch('/research/index.json');
    if (!response.ok) throw new Error(`research register returned ${response.status}`);
    const documents = await response.json();
    if (!documents || documents.length === 0) {
      emptyState();
      return;
    }
    renderRegister(documents);
  } catch (error) {
    errorState(error.message);
  }
}

init();