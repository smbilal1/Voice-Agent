# CareCloud Voice Patient Registration

A Voice AI patient-registration service. This repository is being built in phases for the CareCloud AI Engineer technical assessment.

## Current status

**Phase 3 complete:** patient REST API with validation, filtering, soft deletion, and consistent JSON response envelopes.

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies (including the local API test client):

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`, then add the Phase 0 values when available.
4. Run the API:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Visit:

   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`
   - Dashboard: `http://localhost:8000/`

## Project structure

```text
app/
  api/          # HTTP routes
  core/         # configuration and logging
  db/           # database setup and migrations (Phase 2)
  models/       # SQLAlchemy database models (Phase 2)
  repositories/ # database access (Phase 2)
  schemas/      # Pydantic request/response models (Phase 2)
  services/     # domain and voice-integration logic
  main.py       # FastAPI application factory
```

## Environment variables

See `.env.example`. Never commit `.env` or API credentials.

## Database migrations

After adding your Neon connection string to `.env`, create the database schema:

```bash
alembic upgrade head
```

To create a future migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe_change"
```

The application expects the SQLAlchemy psycopg URL format shown in `.env.example`.

## Patient API

Every endpoint returns `{ "data": ..., "error": null }` on success and a consistent error envelope on failure.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/patients` | List active patients; supports `last_name`, `date_of_birth`, and `phone_number` filters. |
| `GET` | `/patients/{patient_id}` | Retrieve one active patient. |
| `POST` | `/patients` | Create a patient. |
| `PUT` | `/patients/{patient_id}` | Partially update a patient. |
| `DELETE` | `/patients/{patient_id}` | Soft-delete a patient. |

Interactive API documentation is available at `/docs`.

## Dashboard

The server-rendered dashboard at `/` lists active patient registrations and supports filtering by last name, date of birth, and phone number. Select a patient to view their full registration details.

## Vapi setup

Follow the project-specific [Vapi Phase 7 setup guide](docs/vapi-phase-7-setup.md) to create the Assistant and provision the callable U.S. phone number. Keep all Vapi credentials in `.env` locally and in Railway Variables for production.

## Tests

Run the automated API and validation suite with:

```bash
pytest
```

The suite exercises the patient lifecycle, filters, soft deletion, validation, response envelopes, and the PostgreSQL model metadata without requiring a live Neon database.

## Deployment

The supplied `Dockerfile` and `railway.toml` are ready for Railway deployment. On startup, the container applies `alembic upgrade head` before starting Uvicorn, so the Neon schema is current before the service accepts traffic.

### Railway deployment

1. Push this repository to GitHub.
2. In Railway, select **New Project → Deploy from GitHub Repo** and select the repository.
3. Add the environment variables from `.env` in Railway's **Variables** tab. At minimum, set `DATABASE_URL`, `ENVIRONMENT=production`, `LOG_LEVEL=INFO`, and `ALLOWED_ORIGINS` to the deployed public URL.
4. Deploy. Railway will use the included Dockerfile and run the migration automatically.
5. Open the generated public domain and verify `https://YOUR-DOMAIN/health` and `https://YOUR-DOMAIN/docs`.

Never add `.env` or credentials to the repository.

### Vercel deployment

Vercel detects the FastAPI instance in `app/main.py` through `pyproject.toml`; it does **not** use the Dockerfile or run Alembic automatically.

1. Set `DATABASE_URL` locally and run `alembic upgrade head` once to create/update the Neon schema.
2. Push the repository to GitHub, then import it through Vercel's **Add New → Project** flow. Leave the framework preset on **Other** and do not set a build command or output directory.
3. In Vercel **Settings → Environment Variables**, add `DATABASE_URL`, `ENVIRONMENT=production`, `LOG_LEVEL=INFO`, `VAPI_WEBHOOK_SECRET`, `VAPI_API_KEY` (if used), and `ALLOWED_ORIGINS=https://YOUR-PROJECT.vercel.app`.
4. Deploy and verify `/health`, `/docs`, and `/` on the generated Vercel domain.

For the Vapi tool webhook, use `https://YOUR-PROJECT.vercel.app/vapi/tools`.
