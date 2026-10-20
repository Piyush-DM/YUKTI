import { defineConfig } from 'vite';

// Dev-server/bundler only (D1) — no framework plugins, no runtime injected.
// Multi-page build: the homepage, Research Archive, technical-report view,
// and token verification harness are static entry points.
export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        documents: 'documents.html',
        document: 'document.html',
        tokens: 'tokens.html',
      },
    },
  },
});
