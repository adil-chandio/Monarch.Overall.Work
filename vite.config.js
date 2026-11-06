import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';
import path from 'node:path';

function servePortfolioV37() {
  return {
    name: 'serve-portfolio-v37',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const raw = req.url?.split('?')[0] || '';
        if (raw !== '/v37' && raw !== '/v37/') return next();
        const file = path.join(process.cwd(), 'public/v37/index.html');
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(fs.readFileSync(file));
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), servePortfolioV37()],
  server: { host: '0.0.0.0', allowedHosts: ['.e2b.app'] },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom'],
          supabase: ['@supabase/supabase-js'],
          icons: ['lucide-react'],
        },
      },
    },
  },
});
