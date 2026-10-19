# Game Theory Simulator

A platform for simulating strategy tournaments across game-theory games, with a
FastAPI backend, PostgreSQL persistence, and a Next.js dashboard. The first
supported game is the round-robin Iterated Prisoner's Dilemma.

Choose strategies, rounds per match, and matches per pairing. Setting matches per
pairing to 5 runs every pair five times and combines their scores in the leaderboard.

## Project layout

- `backend/`: FastAPI API, simulation engine, database migrations, and tests.
- `frontend/`: Next.js dashboard.
- `compose.yaml`: local API and PostgreSQL services.
- `legacy/`: local archive of the original Pygame application, tests, and logs.
  This directory is Git-ignored and is not included in fresh clones. The original
  files remain available in Git history.

## Run

```bash
cp .env.example .env
# Set POSTGRES_PASSWORD in .env.
docker compose up --build -d
```

In another terminal:

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## API

All routes are under `/api/v1`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API/database status |
| `GET` | `/strategies` | Available strategies |
| `POST` | `/tournaments` | Run and save a tournament |
| `GET` | `/tournaments` | List saved tournaments |
| `GET` | `/tournaments/{id}` | Get a saved tournament |
| `GET` | `/matches/{id}` | Get match rounds and scores |

Example:

```bash
curl -X POST http://localhost:8000/api/v1/tournaments \
  -H 'Content-Type: application/json' \
  -d '{"strategies":["tit_for_tat","always_defect"],"rounds":100,"seed":42}'
```

## Checks

Backend:

```bash
python -m pip install -e './backend[test]'
python -m pytest backend/tests
```

Frontend:

```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

PostgreSQL integration tests require `TEST_DATABASE_URL`; otherwise they are skipped.
