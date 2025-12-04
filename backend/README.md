# Talent Scout AI Backend

FastAPI backend for job posting management with embeddings and employee matching.

## Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Note**: By default, this uses HuggingFace Inference API (no local model needed, works on any CPU). 
If you want to use a local model instead, also install:
```bash
pip install -r requirements-local.txt
```

2. **Set environment variables:**
Create a `.env` file or set these environment variables:
```bash
# Qdrant
QDRANT_URL=https://your-qdrant-url.com
QDRANT_API_KEY=your-qdrant-api-key

# Modal
LLM_MODAL_URL=https://farahalmashad75--job-posting-generator-llama-fastapi-app.modal.run
CLASSIFICATION_MODEL_URL=https://farahalmashad75--promotion-predictor-fastapi-app.modal.run  # Optional (has default)

# Embeddings (choose one):
# Option 1: Use HuggingFace API (recommended for CPU-only, faster, no model download)
HUGGINGFACE_API_KEY=hf_your-token-here
USE_LOCAL_EMBEDDING_MODEL=false

# Option 2: Use local model (slower on CPU, requires PyTorch)
USE_LOCAL_EMBEDDING_MODEL=true
```

3. **Run the server:**
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health check
- `POST /api/generate-job-posting` - Generate job posting using Modal LLM
- `POST /api/approve-posting` - Approve posting, generate embedding, upload to Qdrant, find similar employees

## Features

- ✅ Uses `Supabase/gte-small` model (384D embeddings) - same as your working Python code
- ✅ Qdrant integration for vector storage and similarity search
- ✅ Modal LLM integration for job posting generation
- ✅ Modal classification model for promotion predictions
- ✅ CORS enabled for React frontend

## Embedding Options

### Option 1: HuggingFace API (Recommended for CPU-only laptops) ⭐
- **Pros**: Fast, no model download, works on any CPU, free tier available
- **Cons**: Requires internet connection
- **Setup**: Just set `HUGGINGFACE_API_KEY` and `USE_LOCAL_EMBEDDING_MODEL=false`

### Option 2: Local Model (CPU compatible)
- **Pros**: Works offline, same as your Python code
- **Cons**: Slower on CPU, requires ~100MB download, needs PyTorch
- **Setup**: Install `requirements-local.txt` and set `USE_LOCAL_EMBEDDING_MODEL=true`

**Recommendation**: Use HuggingFace API for CPU-only systems - it's faster and easier!

