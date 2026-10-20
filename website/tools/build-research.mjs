/*
  YUKTI Website — Research Archive data build.

  Reads the publication drafts in research/public/ and emits the JSON the
  Research Archive pages consume. Run via `npm run build:research`.

  This exists because the archive must never restate research by hand: the
  site's copy of a document is derived from the published Markdown, so the
  two cannot drift. Nothing here interprets content — it only converts the
  Markdown subset the publication template uses into HTML.
*/

import { readFileSync, writeFileSync, readdirSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const SRC = join(REPO, 'research', 'public');
const OUT = join(HERE, '..', 'public', 'research');

/* ---------- inline markdown ---------- */

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;' };
const esc = (s) => s.replace(/[&<>]/g, (c) => ESC[c]);
const escAttr = (s) => esc(s).replace(/"/g, '&quot;').replace(/'/g, '&#039;');

// Order matters: code spans are extracted first so their contents are never
// treated as emphasis or link syntax.
function inline(raw) {
  const code = [];
  let s = raw.replace(/`([^`]+)`/g, (_, c) => {
    code.push(c);
    return `\u0000${code.length - 1}\u0000`;
  });

  s = esc(s);
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, href) => {
    const publishedId = publicationLinks.get(href);
    const safe = publishedId
      ? `/document.html?id=${encodeURIComponent(publishedId)}`
      : /^(https?:|mailto:|#|\.|\/)/.test(href) ? href : '#';
    return `<a href="${escAttr(safe)}">${text}</a>`;
  });
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>');

  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(code[Number(i)])}</code>`);
}

/* ---------- block markdown ---------- */

const isTableRow = (l) => l.trim().startsWith('|');
const isDivider = (l) => /^\|[\s|:-]+\|?$/.test(l.trim());
const cells = (l) =>
  l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());

function renderTable(rows) {
  const head = cells(rows[0]);
  const body = rows.slice(2).map(cells);
  // The publication front matter uses a headerless 2-column table; rendering
  // an empty <thead> there would put a blank band above the metadata.
  const headless = head.every((c) => c === '');
  const thead = headless
    ? ''
    : `<thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead>`;
  const tbody = body
    .map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`)
    .join('');
  return `<div class="yukti-doc__tablewrap"><table>${thead}<tbody>${tbody}</tbody></table></div>`;
}

function toHtml(md) {
  const lines = md.split('\n');
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) { i++; continue; }

    if (line.startsWith('```')) {
      const buf = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) buf.push(lines[i++]);
      i++;
      out.push(`<pre><code>${esc(buf.join('\n'))}</code></pre>`);
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      out.push('<hr class="yukti-rule--tick" />');
      i++;
      continue;
    }

    const h = line.match(/^(#{2,4})\s+(.*)$/);
    if (h) {
      const lvl = h[1].length;
      out.push(`<h${lvl}>${inline(h[2])}</h${lvl}>`);
      i++;
      continue;
    }

    if (isTableRow(line) && i + 1 < lines.length && isDivider(lines[i + 1])) {
      const rows = [];
      while (i < lines.length && isTableRow(lines[i])) rows.push(lines[i++]);
      out.push(renderTable(rows));
      continue;
    }

    if (line.trimStart().startsWith('> ')) {
      const buf = [];
      while (i < lines.length && lines[i].trimStart().startsWith('>')) {
        buf.push(lines[i].trimStart().replace(/^>\s?/, ''));
        i++;
      }
      out.push(`<blockquote>${toHtml(buf.join('\n'))}</blockquote>`);
      continue;
    }

    const bullet = /^\s*[-*]\s+/;
    const numbered = /^\s*\d+\.\s+/;
    if (bullet.test(line) || numbered.test(line)) {
      const ordered = numbered.test(line);
      const re = ordered ? numbered : bullet;
      const items = [];
      while (i < lines.length && re.test(lines[i])) {
        let item = lines[i].replace(re, '');
        i++;
        // fold indented continuation lines into the same item
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !re.test(lines[i])) {
          item += ' ' + lines[i].trim();
          i++;
        }
        items.push(`<li>${inline(item)}</li>`);
      }
      out.push(`<${ordered ? 'ol' : 'ul'}>${items.join('')}</${ordered ? 'ol' : 'ul'}>`);
      continue;
    }

    const para = [];
    while (
      i < lines.length && lines[i].trim() &&
      !lines[i].startsWith('#') && !isTableRow(lines[i]) &&
      !lines[i].startsWith('```') && !lines[i].trimStart().startsWith('>') &&
      !bullet.test(lines[i]) && !numbered.test(lines[i]) &&
      !/^---+$/.test(lines[i].trim())
    ) para.push(lines[i++]);
    if (para.length) out.push(`<p>${inline(para.join(' '))}</p>`);
  }

  return out.join('\n');
}

/* ---------- document parsing ---------- */

function parseDoc(md, filename) {
  const lines = md.split('\n');

  const titleLine = lines.findIndex((l) => l.startsWith('# '));
  const title = titleLine >= 0 ? lines[titleLine].replace(/^#\s+/, '').trim() : filename;

  // Front matter is the first headerless table; each row is | **Key** | Value |
  const meta = {};
  for (const l of lines.slice(0, 40)) {
    const m = l.match(/^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|$/);
    if (m) meta[m[1].trim()] = m[2].trim();
  }

  // Body sections, split on H2. Everything before the first H2 is front matter.
  const sections = [];
  let cur = null;
  for (let i = titleLine + 1; i < lines.length; i++) {
    const h2 = lines[i].match(/^##\s+(.*)$/);
    if (h2) {
      if (cur) sections.push(cur);
      cur = { heading: h2[1].trim(), lines: [] };
    } else if (cur) {
      cur.lines.push(lines[i]);
    }
  }
  if (cur) sections.push(cur);

  const built = sections.map((s) => ({
    heading: s.heading,
    slug: s.heading.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
    html: toHtml(s.lines.join('\n')),
    text: s.lines.join(' ').replace(/[#*`|>_[\]()]/g, ' ').replace(/\s+/g, ' ').trim(),
  }));

  const abstract = built.find((s) => /abstract/i.test(s.heading));

  return {
    id: (meta['Document ID'] || '').trim(),
    title,
    series: meta['Series'] || '',
    revision: meta['Revision'] || '',
    status: meta['Status'] || '',
    lastUpdated: meta['Last Updated'] || '',
    source: (meta['Source'] || '').replace(/`/g, ''),
    abstract: abstract ? abstract.text : '',
    sections: built.map(({ heading, slug, html }) => ({ heading, slug, html })),
  };
}

/* ---------- build ---------- */

mkdirSync(OUT, { recursive: true });

const files = readdirSync(SRC).filter((f) => f.endsWith('.md')).sort();
const publicationLinks = new Map(
  files.map((f) => {
    const source = readFileSync(join(SRC, f), 'utf8');
    const id = source.match(/^\|\s*\*\*Document ID\*\*\s*\|\s*(.*?)\s*\|$/m)?.[1].trim();
    return [f, id];
  }).filter(([, id]) => id)
);
const index = [];

for (const f of files) {
  const doc = parseDoc(readFileSync(join(SRC, f), 'utf8'), f);
  if (!doc.id) {
    console.warn(`  SKIP ${f} — no Document ID in front matter`);
    continue;
  }
  writeFileSync(join(OUT, `${doc.id}.json`), JSON.stringify(doc));
  index.push({
    id: doc.id,
    title: doc.title,
    series: doc.series,
    revision: doc.revision,
    status: doc.status,
    lastUpdated: doc.lastUpdated,
    source: doc.source,
    abstract: doc.abstract,
    sections: doc.sections.length,
  });
}

// Sort by series (research, then decisions, then proposals), then by id.
const SERIES_ORDER = ['CHOIR Research Programme', 'Architecture Decisions', 'CHOIR Research Proposals'];
index.sort((a, b) => {
  const s = SERIES_ORDER.indexOf(a.series) - SERIES_ORDER.indexOf(b.series);
  return s !== 0 ? s : a.id.localeCompare(b.id);
});

writeFileSync(join(OUT, 'index.json'), JSON.stringify(index, null, 1));

const byStatus = index.reduce((m, d) => ({ ...m, [d.status]: (m[d.status] || 0) + 1 }), {});
console.log(`research archive: ${index.length} documents -> website/public/research/`);
console.log('  status:', JSON.stringify(byStatus));
