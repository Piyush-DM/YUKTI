/*
  EntrySequence — Addendum v1.3 (architecture §17, Motion Addendum §17).
  State machine only — all visual states are CSS classes, this just toggles
  them at the right moments and handles the session gate + interaction.

  Session gate: sessionStorage (per browser session, not permanent). The
  actual "show the cover" decision already happened synchronously in
  index.html's inline <head> script (adds html.yukti-entry-pending before
  first paint, avoiding any flash) — this module only runs the sequence once
  triggered, and marks the session as seen so a same-session reload/return
  skips straight to the homepage via that same inline script next time.
*/

import { prefersReducedMotion } from './motion-constants.js';

const STORAGE_KEY = 'yukti-entry-seen';

function markSeen() {
  try {
    sessionStorage.setItem(STORAGE_KEY, '1');
  } catch (e) {
    // sessionStorage unavailable (private mode, etc.) — sequence will simply
    // replay on next load, which is a safe degradation, not a broken state.
  }
}

function initEntrySequence() {
  const html = document.documentElement;
  if (!html.classList.contains('yukti-entry-pending')) return; // already seen, or JS-disabled fallback

  const cover = document.querySelector('[data-entry-cover]');
  if (!cover) return;

  let triggered = false;
  const timers = [];

  function detachListeners() {
    cover.removeEventListener('click', trigger);
    window.removeEventListener('keydown', onKeydown);
    window.removeEventListener('wheel', onWheel);
    window.removeEventListener('touchmove', onTouchMove);
  }

  function runReducedFade() {
    // "A simple fade transition while preserving the same visual hierarchy" —
    // no doors, no logo choreography, one shared fade.
    cover.classList.add('is-reduced-fade');
    html.classList.remove('yukti-entry-pending'); // homepage fades in under the same shared duration
    timers.push(setTimeout(() => cover.remove(), 700));
  }

  function runFullSequence() {
    // 0.0s — interaction (this call)
    // 0.2s — subtle acknowledgement
    cover.classList.add('is-acknowledging');
    timers.push(setTimeout(() => cover.classList.remove('is-acknowledging'), 200));

    // 0.4s (via CSS transition-delay) — doors begin splitting
    cover.classList.add('is-splitting');

    // 1.2s — logo begins moving forward
    timers.push(
      setTimeout(() => {
        cover.classList.add('is-advancing');
      }, 1200)
    );

    // 1.8s — homepage starts fading in
    timers.push(
      setTimeout(() => {
        html.classList.remove('yukti-entry-pending');
      }, 1800)
    );

    // ~2.5s — sequence fully resolved; remove the cover so it can never
    // intercept input or linger in the accessibility tree.
    timers.push(
      setTimeout(() => {
        cover.remove();
      }, 2500)
    );
  }

  function trigger() {
    if (triggered) return;
    triggered = true;
    markSeen();
    detachListeners();
    if (prefersReducedMotion()) {
      runReducedFade();
    } else {
      runFullSequence();
    }
  }

  function onKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
      event.preventDefault();
      trigger();
    }
  }

  function onWheel() {
    trigger();
  }

  function onTouchMove() {
    trigger();
  }

  cover.addEventListener('click', trigger);
  window.addEventListener('keydown', onKeydown);
  window.addEventListener('wheel', onWheel, { passive: true });
  window.addEventListener('touchmove', onTouchMove, { passive: true });

  // Native button focus gives Enter/Space for free; explicit focus ensures
  // that works immediately on load without requiring a prior Tab press.
  cover.focus();
}

initEntrySequence();
