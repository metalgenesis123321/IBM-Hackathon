# IBM-Hackathon

> A multi-component hackathon project combining a Python NLP parser backend with a frontend app and transcript/data assets.

## Table of contents
- [About](#about)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
  - [Clone](#clone)
  - [Backend (nlp-parser)](#backend-nlp-parser)
  - [Frontend (frontend)](#frontend-frontend)
- [Transcripts / Data](#transcripts--data)
- [API](#api)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [Development notes & tips](#development-notes--tips)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## About
This repository contains the code and assets developed for the IBM hackathon project. It includes:
- `nlp-parser` — the Python natural language processing backend/service.
- `frontend` — the UI application (likely React/Node based).
- `transcripts` — sample transcripts or data used for processing/analysis.

---

## Features
- Upload or load transcripts and parse them with an NLP pipeline.
- Extract intents/entities / summarize or index conversations.
- Frontend interface to view transcripts, results and interact with the NLP backend.
- Easy local dev and Docker support.

---

## Architecture
```
+--------------+       HTTP/REST       +--------------+
|   Frontend   | <------------------>  |  nlp-parser  |
| (frontend/)  |                       | (Python API) |
+--------------+                       +--------------+
        |
        v
  Browser / User
```

---

## Prerequisites
- Python 3.8+ (for `nlp-parser`)
- Node 14+ / npm or yarn (for `frontend`)
- Docker (optional, if you prefer containers)
- Git

---

## Quick start

### 1) Clone the repo
```bash
git clone https://github.com/metalgenesis123321/IBM-Hackathon.git
cd IBM-Hackathon
```

### 2) Backend — `nlp-parser`
```bash
cd nlp-parser
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
python app.py  # replace with actual entrypoint if different
```

### 3) Frontend — `frontend`
```bash
cd ../frontend
npm install
npm start
```

---

## Transcripts / Data
The `transcripts` folder contains example transcript files used by the NLP pipeline. You can add new transcripts or test with existing ones.

---

## API (example)
```
POST /api/parse
  - body: { "transcript": "<TEXT>" }
  - returns: { "entities": [...], "intents": [...], "summary": "..." }

GET /api/transcripts
  - returns: list of available transcripts

GET /api/transcripts/:id
  - returns: transcript content and parsed output
```

Example:
```bash
curl -X POST http://localhost:5000/api/parse   -H "Content-Type: application/json"   -d '{"transcript": "Hello — this is an example transcript."}'
```

---

## Running with Docker

**Backend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY nlp-parser/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY nlp-parser/ .
CMD ["python", "app.py"]
```

**Frontend Dockerfile**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
```

---

## Testing
```bash
# backend (pytest)
cd nlp-parser
pytest

# frontend (jest)
cd frontend
npm test
```

---

## Development notes & tips
- Enable CORS on backend during development.
- Keep a `.env` for environment variables.
- Example `.env` variables:
  ```
  FLASK_ENV=development
  PORT=5000
  SECRET_KEY=dev-secret
  ```

---

## Contributing
1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/awesome-stuff`.
3. Commit changes: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin feature/awesome-stuff`.
5. Open a Pull Request.

---

## License
MIT License

---

## Acknowledgements
- IBM Hackathon participants and mentors.
- Open-source libraries used in the project.
