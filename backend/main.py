from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
from datetime import datetime
import uuid

# Import embedding and Qdrant functions
from services.embeddings import get_embedding
from services.qdrant_service import upload_to_qdrant, query_similar_employees, check_collection, get_recent_job_postings
from services.modal_service import call_llm, call_classification_model

app = FastAPI(title="Talent Scout AI Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GeneratePostingRequest(BaseModel):
    jobTitle: str
    careerLevel: str
    location: str
    department: str
    keySkills: Optional[str] = None

class ApprovePostingRequest(BaseModel):
    naturalPosting: str
    structuredData: str  # JSON string
    originalInput: Dict[str, Any]

class Employee(BaseModel):
    id: str
    name: str
    department: str
    current_role: str
    similarity_score: float
    promotion_probability: float
    email: str

class ApprovePostingResponse(BaseModel):
    posting: Dict[str, Any]
    similarEmployees: List[Employee]
    qdrant_upload_success: bool

@app.get("/")
async def root():
    return {"message": "Talent Scout AI Backend API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/job-postings")
async def get_job_postings():
    """Get the most recent job postings from Qdrant"""
    try:
        postings = await get_recent_job_postings(limit=10)
        return {"postings": postings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job postings: {str(e)}")

@app.post("/api/generate-job-posting")
async def generate_job_posting(request: GeneratePostingRequest):
    """Generate job posting using Modal LLM"""
    try:
        user_input = f"""Job Title: {request.jobTitle}
Career Level: {request.careerLevel}
Location: {request.location}
Department: {request.department}"""
        
        if request.keySkills:
            user_input += f"\nKey Skills: {request.keySkills}"
        
        # Call Modal LLM
        result = await call_llm(user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating posting: {str(e)}")

@app.post("/api/approve-posting", response_model=ApprovePostingResponse)
async def approve_posting(request: ApprovePostingRequest):
    """Approve posting, generate embedding, upload to Qdrant, and find similar employees"""
    try:
        # Parse structured data
        parsed_data = json.loads(request.structuredData)
        
        # Process skills
        skills = []
        if isinstance(parsed_data.get('skills'), str):
            skills = [s.strip() for s in parsed_data['skills'].split(',')]
        elif isinstance(parsed_data.get('skills'), list):
            skills = parsed_data['skills']
        
        # Generate UUID for Qdrant point ID (Qdrant requires UUID or unsigned integer)
        posting_id = str(uuid.uuid4())
        # Generate job ID in format JOB_XXXX for the payload (where XXXX is a random 4-digit number)
        import random
        job_number = random.randint(1000, 9999)
        job_id = f"JOB_{job_number}"
        date_created = datetime.now().isoformat()
        
        posting = {
            "id": job_id,  # Use JOB_XXXX format for the posting ID
            "job_title": request.originalInput.get('jobTitle'),
            "career_level": request.originalInput.get('careerLevel'),
            "location": request.originalInput.get('location'),
            "department": request.originalInput.get('department'),
            "key_skills": request.originalInput.get('keySkills', '').split(',') if request.originalInput.get('keySkills') else [],
            "natural_posting": request.naturalPosting,
            "structured_data": parsed_data,
            "date_created": date_created,
        }
        
        # Create embedding text
        embedding_text = create_embedding_text(parsed_data, request.naturalPosting)
        print(f"📝 Created embedding text, length: {len(embedding_text)}")
        
        # Check Qdrant collection dimensions
        collection_info = await check_collection()
        print(f"📊 Qdrant collection expects {collection_info['vectorSize']} dimensions")
        
        # Get embedding using Python model
        print("🔄 Generating embedding...")
        embedding = await get_embedding(embedding_text, collection_info['vectorSize'])
        print(f"✅ Got embedding, dimensions: {len(embedding)}")
        
        # Process departments
        department_keywords = process_departments(parsed_data.get('job_categories', ''))
        primary_department = department_keywords[0] if department_keywords else 'General'
        
        # Upload to Qdrant
        print("📤 Uploading to Qdrant...")
        # Set company name to HR Agent Startup
        parsed_data['company'] = 'HR Agent Startup'
        
        qdrant_success = await upload_to_qdrant(
            posting_id=posting_id,  # Use UUID for Qdrant point ID
            job_id=job_id,  # Use JOB_XXXX format for job_id in payload
            embedding=embedding,
            posting_data={
                **posting,
                **parsed_data,  # Include all parsed data fields (title, company, etc.)
                "department_keywords": department_keywords,
                "primary_department": primary_department,
                "skills": skills,
                "embedding_text": embedding_text,
                "is_new_posting": True  # Explicitly set flag
            }
        )
        
        if not qdrant_success:
            raise HTTPException(status_code=500, detail="Failed to upload to Qdrant")
        
        # Query similar employees
        print("🔍 Querying for similar employees...")
        similar_employees_data = await query_similar_employees(embedding, limit=5)
        print(f"✅ Found {len(similar_employees_data)} similar employees")
        
        # Add promotion predictions if classification model URL is available
        # Import here to use the default from modal_service if env var not set
        from services.modal_service import CLASSIFICATION_MODEL_URL as CLASSIFICATION_URL
        similar_employees = similar_employees_data
        if CLASSIFICATION_URL and similar_employees_data:
            try:
                print("🔄 Getting promotion predictions...")
                similar_employees = await add_promotion_predictions(similar_employees_data)
                print("✅ Added promotion predictions")
            except Exception as e:
                print(f"⚠️ Promotion prediction failed: {e}, using default values")
                # Add default promotion probability if prediction fails
                similar_employees = [
                    {**emp, "promotion_probability": 0.6 + (i * 0.05)} 
                    for i, emp in enumerate(similar_employees_data)
                ]
        else:
            # Add default promotion probability if classification model URL is not set
            print("⚠️ No classification model URL configured, using default promotion probabilities")
            similar_employees = [
                {**emp, "promotion_probability": 0.6 + (i * 0.05)} 
                for i, emp in enumerate(similar_employees_data)
            ]
        
        return ApprovePostingResponse(
            posting=posting,
            similarEmployees=similar_employees,
            qdrant_upload_success=True
        )
        
    except Exception as e:
        print(f"❌ ERROR in approve-posting: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error approving posting: {str(e)}")

def create_embedding_text(structured_data: dict, natural_posting: str) -> str:
    """Create text for embedding from structured data and natural posting"""
    skills = structured_data.get('skills', '')
    if isinstance(skills, list):
        skills = ', '.join(skills)
    
    return f"""
Job Title: {structured_data.get('title', '')}
Job Type: {structured_data.get('job_type', '')}
Work Setting: {structured_data.get('work_setting', '')}
Location: {structured_data.get('location', '')}
Experience Level: {structured_data.get('experience_needed', '')}
Career Level: {structured_data.get('career_level', '')}
Education Required: {structured_data.get('education_level', '')}
Department/Categories: {structured_data.get('job_categories', '')}
Required Skills: {skills}

Job Description:
{natural_posting}

Job Requirements:
{natural_posting}
""".strip()

def process_departments(raw_categories: str) -> List[str]:
    """Process department categories into keywords"""
    if not raw_categories:
        return ['General']
    
    processed = raw_categories.replace(' - ', ',').replace(' / ', ',').replace('/', ',').replace('-', ',')
    keywords = [k.strip() for k in processed.split(',') if k.strip()]
    return keywords if keywords else ['General']

async def add_promotion_predictions(employees: List[Dict]) -> List[Dict]:
    """Add promotion probability predictions using Modal classification model"""
    employee_features = [
        {
            "previous_year_rating": emp.get('previous_year_rating', 0),
            "length_of_service": emp.get('length_of_service', 0),
            "awards_won": emp.get('awards_won', 0),
            "no_of_trainings": emp.get('no_of_trainings', 0),
            "avg_training_score": emp.get('avg_training_score', 0),
            "KPIs_met_more_than_80": emp.get('KPIs_met_more_than_80', 0),
            "department": emp.get('department', 'Unknown')
        }
        for emp in employees
    ]
    
    predictions = await call_classification_model(employee_features)
    
    return [
        {**emp, "promotion_probability": pred.get('probability', 0.5)}
        for emp, pred in zip(employees, predictions)
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

