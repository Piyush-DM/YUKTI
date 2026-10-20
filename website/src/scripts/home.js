/* =============================================================
   YUKTI homepage behaviour. Plain script, no imports, `defer`.
   ============================================================= */
(function () {
  'use strict';

  /* ----- waitlist submit destination -------------------------------------
     Set this to the Calendly link (or form endpoint) once it exists.
     - A URL  -> the browser navigates there on a valid submit.
     - Empty  -> the form shows an inline confirmation; no data leaves the page.
     -------------------------------------------------------------------- */
  var ACCESS_URL = '';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----- mobile nav ---------------------------------------------------- */
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav__toggle');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('.nav__links a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ----- layers: highlight the matching plane on hover / focus -------- */
  var diagram = document.querySelector('.layers__diagram');
  var items = document.querySelectorAll('.layer-list__item');
  if (diagram && items.length) {
    var planes = diagram.querySelectorAll('.plane');
    var lightFor = function (el) {
      var layer = el ? el.getAttribute('data-layer') : null;
      planes.forEach(function (p) {
        p.classList.toggle('is-lit', !!layer && p.getAttribute('data-plane') === layer);
      });
      items.forEach(function (it) { it.classList.toggle('is-active', it === el); });
    };
    items.forEach(function (it) {
      it.addEventListener('mouseenter', function () { lightFor(it); });
      it.addEventListener('focus', function () { lightFor(it); });
      it.addEventListener('mouseleave', function () { lightFor(null); });
      it.addEventListener('blur', function () { lightFor(null); });
    });
  }

  /* ----- reveal on scroll ------------------------------------------------ */
  var revealables = document.querySelectorAll('[data-reveal]');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-revealed'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ----- waitlist form ------------------------------------------------- */
  var form = document.querySelector('.wl');
  if (form) {
    var status = form.querySelector('.wl__status');
    var say = function (msg, isError) {
      if (!status) return;
      status.textContent = msg;
      status.hidden = false;
      status.classList.toggle('is-error', !!isError);
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = form.elements.name.value.trim();
      var email = form.elements.email.value.trim();
      var firm = form.elements.firm.value.trim();
      var role = form.elements.role.value;
      var emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      if (!name || !firm || !role) { say('Please complete every field.', true); return; }
      if (!emailOk) { say('Please enter a valid work email.', true); return; }

      if (ACCESS_URL) {
        say('Opening the next step…', false);
        window.location.href = ACCESS_URL;
        return;
      }
      form.querySelectorAll('input, select, button').forEach(function (el) { el.disabled = true; });
      say('Thank you — you are on the list. We will be in touch.', false);
    });
  }
})();
