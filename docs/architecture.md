# Architecture

## Product flow

Find → Understand → Filter → Match → Prepare → Track

## MVP flow

1. User signs in.
2. User creates a tender record.
3. User uploads a tender PDF.
4. Backend records processing status.
5. Text extraction and AI analysis produce structured results.
6. User reviews requirements and verifies important fields.
7. Contractor profile is matched requirement-by-requirement.

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + Python
- Database/Auth/Storage: Supabase
- Deployment: Vercel + Render

AI output should be validated into structured schemas before persistence. The AI service should not write arbitrary database records directly.
