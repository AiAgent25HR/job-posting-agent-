"""
Qdrant service for vector database operations
"""
import os
import httpx
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

QDRANT_URL = os.getenv('QDRANT_URL', 'https://f04ab44d-7efd-4966-8ba7-1e5334332422.eu-central-1-0.aws.cloud.qdrant.io')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TKp2mJG6GOdU-XaaknAlcC1iDjiKdugLvhDD1C1K9Xk')
JOB_POSTINGS_COLLECTION = 'job_postings_cluster'
EMPLOYEES_COLLECTION = 'employees'

def get_headers():
    return {
        'Content-Type': 'application/json',
        'api-key': QDRANT_API_KEY
    }

async def check_collection(collection_name: str = JOB_POSTINGS_COLLECTION) -> Dict[str, Any]:
    """Check Qdrant collection configuration and return vector size"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{QDRANT_URL}/collections/{collection_name}",
                headers=get_headers()
            )
        
            if not response.is_success:
                print(f"⚠️ Collection {collection_name} not found or error, assuming 384 dimensions")
                return {"vectorSize": 384}
            
            data = response.json()
        vector_size = data.get('result', {}).get('config', {}).get('params', {}).get('vectors', {}).get('size', 384)
        print(f"📊 Collection {collection_name} expects {vector_size} dimensions")
        return {"vectorSize": vector_size}
    except Exception as e:
        print(f"⚠️ Error checking collection: {e}, assuming 384 dimensions")
        return {"vectorSize": 384}

async def upload_to_qdrant(
    posting_id: str,  # UUID for Qdrant point ID
    job_id: str,  # JOB_XXXX format for job_id in payload
    embedding: List[float],
    posting_data: Dict[str, Any]
) -> bool:
    """Upload job posting with embedding to Qdrant"""
    try:
        payload = {
            "points": [{
                "id": posting_id,  # UUID for Qdrant point ID
                "vector": embedding,
                "payload": {
                    "job_id": job_id,  # JOB_XXXX format
                    "status": "active",
                    "date_created": posting_data.get('date_created') or datetime.now().isoformat(),
                    "is_new_posting": True,  # Always True for newly created postings
                    "title": posting_data.get('title') or posting_data.get('job_title', ''),
                    "company": posting_data.get('company', 'HR Agent Startup'),  # Default company name
                    "job_type": posting_data.get('job_type', ''),
                    "work_setting": posting_data.get('work_setting', ''),
                    "location": posting_data.get('location', ''),
                    "experience_needed": posting_data.get('experience_needed', ''),
                    "career_level": posting_data.get('career_level', ''),
                    "education_level": posting_data.get('education_level', ''),
                    "job_categories": posting_data.get('department_keywords', []),
                    "department": posting_data.get('primary_department', 'General'),
                    "skills": posting_data.get('skills', []),
                    "job_description": posting_data.get('natural_posting', ''),
                    "job_requirements": posting_data.get('natural_posting', ''),
                    "embedding_text": posting_data.get('embedding_text', '')
                }
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{QDRANT_URL}/collections/{JOB_POSTINGS_COLLECTION}/points?wait=true",
                headers=get_headers(),
                json=payload
            )
            
            if not response.is_success:
                error_text = response.text
                print(f"❌ Qdrant upload failed: {error_text}")
                return False
            
            print("✅ Job posting uploaded to Qdrant successfully")
            return True
        
    except Exception as e:
        print(f"❌ Error uploading to Qdrant: {e}")
        return False

async def get_collection_count(collection_name: str = EMPLOYEES_COLLECTION) -> int:
    """Get the total number of points in a collection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{QDRANT_URL}/collections/{collection_name}",
                headers=get_headers()
            )
            if response.is_success:
                data = response.json()
                points_count = data.get('result', {}).get('points_count', 0)
                return points_count
    except Exception as e:
        print(f"⚠️ Error getting collection count: {e}")
    return 0

async def query_similar_employees(
    job_embedding: List[float],
    limit: int = 5,
    score_threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """Query Qdrant for similar employees using cosine similarity"""
    try:
        # Check how many employees are in the collection
        total_employees = await get_collection_count(EMPLOYEES_COLLECTION)
        print(f"📊 Total employees in Qdrant collection: {total_employees}")
        
        print(f"🔍 Querying Qdrant for employees (limit={limit}, threshold={score_threshold})")
        payload = {
            "vector": job_embedding,
            "limit": limit,
            "with_payload": True,
            "score_threshold": score_threshold
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{QDRANT_URL}/collections/{EMPLOYEES_COLLECTION}/points/search",
                headers=get_headers(),
                json=payload
            )
            
            if not response.is_success:
                error_text = response.text
                print(f"❌ Qdrant search failed: {error_text}")
                return []
            
            result = response.json()
            employees_data = result.get('result', [])
            
            print(f"📊 Qdrant returned {len(employees_data)} employees")
            
            if not employees_data:
                print("⚠️ No similar employees found")
                return []
            
            # Debug: Print first employee payload to see structure
            if employees_data:
                print(f"🔍 Sample employee payload keys: {list(employees_data[0].get('payload', {}).keys())}")
                print(f"🔍 Sample employee payload: {employees_data[0].get('payload', {})}")
            
            employees = []
            for item in employees_data:
                payload_data = item.get('payload', {})
                
                # Map fields based on actual Qdrant payload structure
                # Name: combine first_name and last_name
                first_name = payload_data.get('first_name', '')
                last_name = payload_data.get('last_name', '')
                name = f"{first_name} {last_name}".strip() if (first_name or last_name) else 'Unknown'
                
                # Department: already correct field name
                department = payload_data.get('department', 'Unknown')
                
                # Current role: use job_title
                current_role = payload_data.get('job_title') or payload_data.get('current_role') or 'Unknown'
                
                # Email: already correct field name
                email = payload_data.get('email', f"employee{item.get('id')}@company.com")
                
                # Convert numeric fields (some might be strings)
                def safe_float(value, default=0.0):
                    try:
                        return float(value) if value not in [None, '', 'None'] else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value not in [None, '', 'None'] else default
                    except (ValueError, TypeError):
                        return default
                
                employees.append({
                    "id": str(item.get('id', '')),
                    "name": name,
                    "department": department,
                    "current_role": current_role,
                    "email": email,
                    "similarity_score": item.get('score', 0.0),
                    "previous_year_rating": safe_float(payload_data.get('previous_year_rating'), 0),
                    "length_of_service": safe_float(payload_data.get('length_of_service'), 0),
                    "awards_won": safe_int(payload_data.get('awards_won'), 0),
                    "no_of_trainings": safe_int(payload_data.get('no_of_trainings'), 0),
                    "avg_training_score": safe_float(payload_data.get('avg_training_score'), 0),  # May not exist in payload
                    "KPIs_met_more_than_80": safe_int(payload_data.get('KPIs_met_more_than_80'), 0),  # May not exist in payload
                })
            
            # Sort by similarity score (descending)
            employees.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"✅ Found {len(employees)} similar employees (returning top {min(len(employees), limit)})")
            return employees[:limit]
        
    except Exception as e:
        print(f"❌ Error querying employees: {e}")
        return []

async def get_recent_job_postings(limit: int = 100) -> List[Dict[str, Any]]:
    """Get the most recent job postings from Qdrant (sorted by date_created)"""
    try:
        print(f"🔍 Fetching most recent job postings from Qdrant (limit={limit})...")
        
        # Use scroll API to get all points, then sort by date_created
        async with httpx.AsyncClient() as client:
            # First, get all points using scroll
            scroll_payload = {
                "limit": 10000,  # Get up to 10000 points to ensure we get all postings
                "with_payload": True,
                "with_vector": False
            }
            
            response = await client.post(
                f"{QDRANT_URL}/collections/{JOB_POSTINGS_COLLECTION}/points/scroll",
                headers=get_headers(),
                json=scroll_payload
            )
            
            if not response.is_success:
                error_text = response.text
                print(f"❌ Qdrant scroll failed: {error_text}")
                return []
            
            result = response.json()
            all_points = result.get('result', {}).get('points', [])
            
            print(f"📊 Found {len(all_points)} total job postings in Qdrant")
            
            # Extract postings with date_created
            postings = []
            for point in all_points:
                payload = point.get('payload', {})
                date_created = payload.get('date_created', '')
                
                # Only show postings with is_new_posting flag (newly created ones)
                is_new_posting = payload.get('is_new_posting', False)
                print(f"🔍 Checking posting: job_id={payload.get('job_id')}, is_new_posting={is_new_posting}")
                if not is_new_posting:
                    print(f"⏭️ Skipping posting (is_new_posting=False): {payload.get('job_id')}")
                    continue
                
                # Skip if no date_created
                if not date_created:
                    continue
                
                postings.append({
                    "id": payload.get('job_id') or str(point.get('id', '')),  # Use job_id (JOB_XXXX) if available
                    "job_title": payload.get('title') or payload.get('job_title', 'Untitled'),
                    "career_level": payload.get('career_level', ''),
                    "location": payload.get('location', ''),
                    "department": payload.get('department', 'General'),
                    "key_skills": payload.get('skills', []),
                    "natural_posting": payload.get('job_description', ''),
                    "date_created": date_created,
                    "structured_data": {
                        "title": payload.get('title', ''),
                        "company": payload.get('company', ''),
                        "job_type": payload.get('job_type', ''),
                        "work_setting": payload.get('work_setting', ''),
                        "experience_needed": payload.get('experience_needed', ''),
                        "education_level": payload.get('education_level', ''),
                    }
                })
            
            # Sort by date_created (most recent first)
            postings.sort(key=lambda x: x.get('date_created', ''), reverse=True)
            
            # Return all postings (no limit, show all newly created ones)
            print(f"✅ Returning {len(postings)} job postings (all with is_new_posting=True)")
            return postings
            
    except Exception as e:
        print(f"❌ Error fetching recent job postings: {e}")
        import traceback
        traceback.print_exc()
        return []

