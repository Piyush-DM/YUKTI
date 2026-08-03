/*
  ReasoningCanvas — reserved, empty visualization container.
  Architecture Addendum §15.1. CONTRACT: never contains invented graph
  content (no fake nodes, edges, or diagrams). Only a mount API for the real,
  proprietary reasoning graph to attach to later.

  Usage (future integration):
    import { createReasoningCanvas } from './reasoning-canvas.js';
    const canvas = createReasoningCanvas(document.querySelector('[data-reasoning-canvas]'));
    canvas.mountSVG(theRealGraphSvgElement);
    // or: canvas.mountCanvas(theRealGraphCanvasElement);
    // canvas.clear() removes it and restores the empty/reserved state.
*/

export function createReasoningCanvas(rootEl) {
  const surface = rootEl.querySelector('[data-reasoning-canvas-surface]');

  function clear() {
    surface.innerHTML = '';
    rootEl.classList.remove('is-mounted');
  }

  function mount(el) {
    clear();
    surface.appendChild(el);
    rootEl.classList.add('is-mounted');
  }

  return {
    mountSVG: mount,
    mountCanvas: mount,
    clear,
  };
}

// Documented global integration point — the future reasoning-graph module
// calls window.YUKTI.reasoningCanvas.mountSVG(...)/.mountCanvas(...) rather
// than requiring this container to be rewritten.
const rootEl = document.querySelector('[data-reasoning-canvas]');
if (rootEl) {
  window.YUKTI = window.YUKTI || {};
  window.YUKTI.reasoningCanvas = createReasoningCanvas(rootEl);
}
