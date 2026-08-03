import { defineConfig } from 'vite';

// Dev-server/bundler only (D1) — no framework plugins, no runtime injected.
// Multi-page build: the real homepage (index.html) and the Step 1 token
// verification harness (tokens.html) are both static entry points.
export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        tokens: 'tokens.html',
      },
    },
  },
});
