# Tender Intelligence Platform API

FastAPI backend for tender ingestion, document processing, AI analysis, contractor profiles, and tender matching.

## Local development

```bash
cd backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health endpoint: `GET /api/v1/health`

API documentation: `/docs`
