# BloodLink AI — Netlify frontend + Python API

This adds a static, responsive frontend for Netlify while preserving the original Streamlit app and its Python matching algorithms. The Netlify site does **not** execute Python; the API is a separate service.

## Local testing on macOS

From the repository root, activate your existing virtual environment, then:

```bash
pip install -r requirements-api.txt
uvicorn api.main:app --reload
```

Open a second terminal and serve the static frontend (do not open `index.html` directly, because browser fetch/CORS behavior can vary):

```bash
python3 -m http.server 8080 --directory frontend
```

Visit http://127.0.0.1:8080, click the gear icon, and set the API URL to `http://127.0.0.1:8000`.

API docs: http://127.0.0.1:8000/docs

## Deploy the API first

1. Push this project to GitHub.
2. In Render, create a **New Web Service** and connect the `bloodlink-ai` repository.
3. Use the included `render.yaml`, or configure:
   - Build command: `pip install -r requirements-api.txt`
   - Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
4. After deployment, copy the service base URL (e.g. `https://your-service.onrender.com`).

For a persistent production database, configure a persistent disk or external database before relying on saved records. The included SQLite database is suitable for a demo and may reset on ephemeral hosting. Startup creates synthetic demo records if the database is empty.

## Deploy the frontend on Netlify

1. In Netlify, choose **Add new site → Import an existing project** and select the GitHub repo.
2. Build command: leave empty. Publish directory: `frontend`.
3. Deploy the site.
4. Open the published site, click the gear icon, paste the API service base URL, and choose **Save and reconnect**.
5. If the browser reports a CORS error, set the API environment variable `CORS_ORIGINS` on the API host to your exact Netlify site origin (for example `https://your-site.netlify.app`) and redeploy the API.

## Important safety and limitations

- Educational prototype only. Do not enter real donor/patient data.
- No authentication is included; do not expose sensitive records or use for real operations.
- The compatibility rules are simplified and not a clinical transfusion protocol.
- Authorized staff must verify eligibility, antibody screening, crossmatching and all clinical decisions.
