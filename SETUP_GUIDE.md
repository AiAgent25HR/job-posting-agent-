# 🚀 Setup Guide: FastAPI Backend + React Frontend

## Overview

This setup replaces Supabase Edge Functions with a Python FastAPI backend that:
- Uses your working Python embedding code (`Supabase/gte-small` model)
- Integrates with Qdrant for vector storage
- Calls Modal for LLM and classification models
- Keeps your React frontend unchanged

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: The first time you run this, it will download the `Supabase/gte-small` model (~100MB). Make sure you have enough disk space.

### 1.2 Set Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Qdrant Configuration
QDRANT_URL=https://f04ab44d-7efd-4966-8ba7-1e5334332422.eu-central-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TKp2mJG6GOdU-XaaknAlcC1iDjiKdugLvhDD1C1K9Xk

# Modal URLs
LLM_MODAL_URL=https://farahalmashad75--job-posting-generator-llama-fastapi-app.modal.run
CLASSIFICATION_MODEL_URL=https://farahalmashad75--promotion-predictor-fastapi-app.modal.run  # Optional (has default)
```

### 1.3 Run the Backend

```bash
cd backend
python main.py
```

Or with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Step 2: Frontend Setup

### 2.1 Set API URL

Create a `.env` file in the root directory (same level as `package.json`):

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 2.2 Run the Frontend

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or similar)

## Step 3: Test It

1. **Start the backend**: `cd backend && python main.py`
2. **Start the frontend**: `npm run dev`
3. **Test the flow**:
   - Go to Create Posting
   - Fill in the form
   - Click "Generate Job Posting"
   - Review and click "Approve & Post"
   - You should see similar employees!

## Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Make sure Python 3.8+ is installed

### Frontend can't connect to backend
- Make sure backend is running on `http://localhost:8000`
- Check the `VITE_API_BASE_URL` in your `.env` file
- Check browser console for CORS errors (shouldn't happen, CORS is enabled)

### Embedding model download fails
- Check your internet connection
- Make sure you have enough disk space (~100MB for the model)
- The model is cached after first download

### Qdrant connection fails
- Verify your Qdrant URL and API key in `.env`
- Make sure the collections exist in Qdrant:
  - `job_postings_cluster`
  - `employees`

## File Structure

```
backend/
├── main.py                 # FastAPI app
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── services/
│   ├── __init__.py
│   ├── embeddings.py       # Your working Python embedding code
│   ├── qdrant_service.py  # Qdrant integration
│   └── modal_service.py   # Modal LLM & classification calls
└── README.md

src/
├── lib/
│   └── api.ts             # API client (calls FastAPI)
└── pages/
    ├── CreatePosting.tsx  # Updated to use FastAPI
    └── ReviewPosting.tsx # Updated to use FastAPI
```

## What Changed

✅ **Backend**: Python FastAPI instead of Supabase Edge Functions
✅ **Embeddings**: Uses your working `Supabase/gte-small` Python code
✅ **Frontend**: Minimal changes - just API calls updated
✅ **Qdrant**: Same integration, now in Python
✅ **Modal**: Same LLM and classification model calls

## Next Steps

1. Test the complete flow
2. Add database integration (if needed) - currently returns mock posting data
3. Deploy backend (Railway, Render, Fly.io, etc.)
4. Update frontend API URL for production

## Deployment

### Backend Deployment Options:
- **Railway**: Easy Python deployment
- **Render**: Free tier available
- **Fly.io**: Good for Python apps
- **Heroku**: Classic option

### Frontend Deployment:
- Keep using your current deployment (Lovable, Vercel, etc.)
- Just update `VITE_API_BASE_URL` to point to your deployed backend

