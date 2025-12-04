"""
Modal service for calling LLM and classification model
"""
import os
import httpx
from typing import List, Dict, Any

LLM_MODAL_URL = os.getenv(
    'LLM_MODAL_URL',
    'https://farahalmashad75--job-posting-generator-llama-fastapi-app.modal.run'
)
CLASSIFICATION_MODEL_URL = os.getenv(
    'CLASSIFICATION_MODEL_URL',
    'https://farahalmashad75--promotion-predictor-fastapi-app.modal.run'
)

async def call_llm(user_input: str) -> Dict[str, Any]:
    """Call Modal LLM to generate job posting"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LLM_MODAL_URL,
                json={"user_input": user_input},
                timeout=300.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"❌ Error calling LLM: {e}")
        raise

async def call_classification_model(employee_features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Call Modal classification model for promotion predictions"""
    if not CLASSIFICATION_MODEL_URL:
        # Return mock predictions if no URL configured
        return [{"probability": 0.6 + (i * 0.1)} for i in range(len(employee_features))]
    
    try:
        # Use /predict endpoint if URL doesn't already include it
        endpoint_url = CLASSIFICATION_MODEL_URL
        if not endpoint_url.endswith('/predict'):
            endpoint_url = f"{CLASSIFICATION_MODEL_URL.rstrip('/')}/predict"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint_url,
                json={"employees": employee_features},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list):
                return [{"probability": r.get('probability', 0.5)} if isinstance(r, dict) else {"probability": r} for r in result]
            elif isinstance(result, dict) and 'predictions' in result:
                return result['predictions']
            else:
                return [{"probability": 0.5} for _ in employee_features]
    except Exception as e:
        print(f"⚠️ Error calling classification model: {e}")
        # Return mock predictions on error
        return [{"probability": 0.6 + (i * 0.1)} for i in range(len(employee_features))]

