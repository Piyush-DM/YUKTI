/*
  YUKTI Website — Mobile nav toggle.

  Bug fix (see nav.css): below 759px .yukti-nav__links was display:none with
  the only substitute — the trigger button — shipped disabled. Mobile had no
  working navigation. This wires the trigger to open/close the existing link
  list as a dropdown panel. Vanilla JS only, no dependencies (D1), matching
  the rest of the site's script style — one responsibility, no framework.

  Shared across index.html, documents.html and document.html: each has its
  own header markup with the same [data-nav-trigger] button and #nav-links
  list, so one script covers all three rather than duplicating this logic.
*/

function initNavToggle() {
  const trigger = document.querySelector('[data-nav-trigger]');
  const header = document.querySelector('.yukti-nav');
  const links = document.getElementById('nav-links');
  if (!trigger || !header || !links) return;

  function isOpen() {
    return trigger.getAttribute('aria-expanded') === 'true';
  }

  function open() {
    header.setAttribute('data-nav-open', '');
    trigger.setAttribute('aria-expanded', 'true');
  }

  function close() {
    header.removeAttribute('data-nav-open');
    trigger.setAttribute('aria-expanded', 'false');
  }

  trigger.addEventListener('click', () => {
    if (isOpen()) close();
    else open();
  });

  // A link was just used to navigate; the panel should not still be open
  // over the destination section.
  links.addEventListener('click', (event) => {
    if (event.target.closest('a')) close();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isOpen()) {
      close();
      trigger.focus();
    }
  });

  document.addEventListener('click', (event) => {
    if (isOpen() && !header.contains(event.target)) close();
  });

  // The link list only ever renders under 759px per nav.css; if the
  // viewport is resized past that with the panel open, close it so it
  // doesn't reappear stuck open when the layout narrows again.
  window.addEventListener('resize', () => {
    if (window.innerWidth > 759 && isOpen()) close();
  });
}

initNavToggle();
