const archiveNav = [
  { label: 'Home', href: '/' },
  { label: 'Documents', href: '/documents.html' },
  { label: 'Contact', href: '/#contact' },
];

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

function statusClass(status) {
  return `yukti-status--${status.toLowerCase().replace(/\s+/g, '-')}`;
}

function showSkeleton() {
  const root = document.getElementById('document-root');
  root.setAttribute('aria-busy', 'true');
  root.innerHTML = `
    <div class="yukti-shell">
      <div class="yukti-doc__skeleton" aria-hidden="true">
        <div class="skeleton-line" style="width: 30%; height: 1.5rem; margin-bottom: var(--yukti-space-2);"></div>
        <div class="skeleton-line" style="width: 60%;"></div>
        <div class="skeleton-line" style="width: 40%; margin-bottom: var(--yukti-space-6);"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line" style="width: 80%;"></div>
        <div class="skeleton-line" style="width: 90%;"></div>
        <div class="skeleton-line" style="width: 70%;"></div>
        <div class="skeleton-line" style="width: 50%;"></div>
        <div class="skeleton-line" style="width: 60%; margin-top: var(--yukti-space-4);"></div>
      </div>
    </div>
  `;
}

function errorState(message) {
  const root = document.getElementById('document-root');
  root.removeAttribute('aria-busy');
  root.innerHTML = `
    <div class="yukti-shell yukti-doc__missing">
      <p class="yukti-type-data">DOCUMENT NOT FOUND</p>
      <h1>There is no published sheet for this identifier.</h1>
      <p class="yukti-type-body">${escapeHtml(message)}</p>
      <a class="yukti-quiet-link" href="/documents.html">Return to the document register</a>
    </div>
  `;
}

function emptyState() {
  const root = document.getElementById('document-root');
  root.removeAttribute('aria-busy');
  root.innerHTML = `
    <div class="yukti-shell yukti-doc__empty">
      <h2>No content available</h2>
      <p>The document exists but contains no rendered sections.</p>
    </div>
  `;
}

function documentIndex(index, id) {
  return index.findIndex((item) => item.id === id);
}

function adjacentLink(item, direction) {
  if (!item) return '';
  return `<a class="yukti-quiet-link" href="/document.html?id=${encodeURIComponent(item.id)}">${direction}: ${escapeHtml(item.id)}</a>`;
}

function renderDocument(doc, index) {
  const root = document.getElementById('document-root');
  const position = documentIndex(index, doc.id);
  const total = index.length;
  const previous = index[position - 1];
  const next = index[position + 1];
  const contents = doc.sections
    .map((section) => `<li><a href="#${escapeHtml(section.slug)}">${escapeHtml(section.heading)}</a></li>`)
    .join('');
  const sections = doc.sections
    .map((section) => `<section id="${escapeHtml(section.slug)}"><h2>${escapeHtml(section.heading)}</h2>${section.html}</section>`)
    .join('');

  document.title = `${doc.id} - ${doc.title} | YUKTI`;
  root.removeAttribute('aria-busy');
  root.innerHTML = `
    <div class="yukti-shell">
      <header class="yukti-doc__titleblock">
        <div class="yukti-doc__stamp">
          <span class="yukti-doc__stamp-id">${escapeHtml(doc.id)}</span>
          <span class="yukti-doc__stamp-rev">REV ${escapeHtml(doc.revision)}</span>
          <span class="yukti-status ${statusClass(doc.status)}">${escapeHtml(doc.status)}</span>
        </div>
        <h1 class="yukti-doc__title">${escapeHtml(doc.title)}</h1>
        <dl class="yukti-doc__provenance">
          <div><dt>Series</dt><dd>${escapeHtml(doc.series)}</dd></div>
          <div><dt>Last Updated</dt><dd>${escapeHtml(doc.lastUpdated)}</dd></div>
          <div><dt>Source</dt><dd>${escapeHtml(doc.source)}</dd></div>
        </dl>
      </header>
      <div class="yukti-doc__layout">
        <div class="yukti-doc__body">${sections}</div>
        <nav class="yukti-doc__contents" aria-label="Document contents">
          <h2>Contents</h2>
          <ol>${contents}</ol>
        </nav>
      </div>
      <footer class="yukti-doc__foot">
        <div class="yukti-doc__foot-nav">
          ${adjacentLink(previous, 'Previous')}
          <a class="yukti-quiet-link" href="/documents.html">Register</a>
          ${adjacentLink(next, 'Next')}
        </div>
        <span class="yukti-doc__sheet">SHEET ${String(position + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}</span>
      </footer>
    </div>
  `;
}

async function init() {
  renderNav();
  const id = new URLSearchParams(window.location.search).get('id');
  if (!id || !/^YK-[RDP]-\d{3}$/.test(id)) {
    errorState('Use a document identifier from the archive register.');
    return;
  }

  showSkeleton();

  try {
    const [indexResponse, docResponse] = await Promise.all([
      fetch('/research/index.json'),
      fetch(`/research/${encodeURIComponent(id)}.json`),
    ]);
    if (!indexResponse.ok || !docResponse.ok) throw new Error(`No published document is registered as ${id}.`);
    const [index, doc] = await Promise.all([indexResponse.json(), docResponse.json()]);
    if (!index.some((item) => item.id === doc.id)) throw new Error(`No published document is registered as ${id}.`);
    if (!doc.sections || doc.sections.length === 0) {
      emptyState();
      return;
    }
    renderDocument(doc, index);
  } catch (error) {
    errorState(error.message);
  }
}

init();