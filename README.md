# Typing Consistency Research Prototype

This repository is a CPU-friendly behavioral-biometric research prototype. It
will compare typing-pattern verification methods and provide a local web demo.
Its output is a **typing consistency score**, not proof of identity and not a
replacement for passwords or multi-factor authentication.

Milestone 1 establishes canonical schemas, deterministic configuration, the
event-to-sequence path, the common model contract, research/privacy protocols,
and minimal Python and React/Vite project scaffolds.

## Prerequisites

- Python 3.11
- Node.js 24 and npm 11

The versions above match the environment used to verify Milestone 1. Python is
intentionally constrained to 3.11 in `pyproject.toml`.

## Verified setup and checks

From the repository root on PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pytest
```

For the frontend:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd test
npm.cmd run build
```

The lock files are the reproducible setup inputs. `pyproject.toml` and
`frontend/package.json` declare the direct dependencies; `requirements.lock`
and `frontend/package-lock.json` pin the resolved dependency graphs.

## Repository layout

- `backend/src/keystroke`: shared schemas, configuration, sequence conversion,
  and model lifecycle interfaces.
- `backend/tests`: synthetic fixtures and unit/schema validation tests.
- `config`: checked-in operational defaults, including the project seed.
- `docs`: threat model, data dictionary, experiment protocol, and participant
  data boundaries.
- `frontend`: minimal React/Vite application scaffold. Browser event capture is
  intentionally deferred to Milestone 3.

Generated datasets, participant recordings, databases, derived features,
checkpoints, trained artifacts, and experiment outputs are ignored by Git.
