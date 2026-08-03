/*
  YUKTI Website — Page Motion Behaviors (Motion System Addendum §15.2)
  Vanilla JS only, no dependencies (D1/D7). Three responsibilities, each a
  single function: reveal-on-scroll wiring, blueprint scroll-parallax, and the
  ReasoningCanvas coordinate readout. Every continuous/JS-driven effect checks
  prefersReducedMotion() explicitly, since token-zeroing (tokens.motion.css)
  only covers CSS-transition-driven motion, not rAF/scroll-driven motion
  (Motion Rule 8).
*/

import {
  REVEAL_IO_THRESHOLD,
  REVEAL_STAGGER_SLOTS,
  REVEAL_STAGGER_STEP_MS,
  prefersReducedMotion,
} from './motion-constants.js';

function assignStaggerDelays() {
  document.querySelectorAll('[data-reveal-group]').forEach((group) => {
    const items = group.querySelectorAll('[data-reveal]');
    items.forEach((el, i) => {
      el.style.setProperty(
        '--yukti-reveal-delay',
        `${(i % REVEAL_STAGGER_SLOTS) * REVEAL_STAGGER_STEP_MS}ms`
      );
    });
  });
}

function initRevealOnScroll() {
  assignStaggerDelays();
  const targets = document.querySelectorAll('[data-reveal]');

  if (prefersReducedMotion()) {
    targets.forEach((el) => el.classList.add('is-revealed'));
    return;
  }

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: REVEAL_IO_THRESHOLD }
  );

  targets.forEach((el) => io.observe(el));
}

function initBlueprintParallax() {
  if (prefersReducedMotion()) return;
  const blueprint = document.querySelector('.yukti-blueprint');
  if (!blueprint) return;

  const K = 0.04; // scroll-parallax primitive, Motion Addendum §15.2
  let ticking = false;

  function render() {
    const offset = window.scrollY * K;
    blueprint.style.transform = `translate3d(0, ${(-offset).toFixed(2)}px, 0)`;
    ticking = false;
  }

  window.addEventListener(
    'scroll',
    () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(render);
      }
    },
    { passive: true }
  );
}

function initReasoningCanvasReadout() {
  const canvasEl = document.querySelector('[data-reasoning-canvas]');
  const readout = canvasEl && canvasEl.querySelector('[data-coordinate-readout]');
  if (!canvasEl || !readout) return;

  // Addendum v1.2: integer pixel offsets, not normalized 0–1 fractions —
  // reads closer to a real instrument readout (matches the brief's mockup).
  canvasEl.addEventListener('mousemove', (event) => {
    const rect = canvasEl.getBoundingClientRect();
    const x = Math.round(event.clientX - rect.left);
    const y = Math.round(event.clientY - rect.top);
    readout.textContent = `X ${x}  Y ${y}`;
  });

  canvasEl.addEventListener('mouseleave', () => {
    readout.textContent = 'X —  Y —';
  });
}

initRevealOnScroll();
initBlueprintParallax();
initReasoningCanvasReadout();
