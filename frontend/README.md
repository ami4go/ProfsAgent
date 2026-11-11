# ProfsAgent frontend

The professor-facing app. Source here; the build is written to `../src/profsagent/app/static/ui` and served by
`scripts/run_app.py`. The design system, the file map and the principles are in **`../docs/11_frontend.md`**.

```bash
npm install
npm run dev        # http://localhost:5173 — needs the app on port 8000 (python scripts/run_app_demo.py works without AI keys)
npm run build      # tsc --noEmit, then vite build into the Python package (commit the result)
npm test           # vitest
```
