from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Model Production Inference Engine")

class CustomerDataInput(BaseModel):
    customer_name: str = Field(..., description="Name of the customer", examples=["Majid Hussain"])
    
    monthly_spend: float = Field(..., gt=0.0, description="Monthly spending in USD", examples=[79.99])
    tenure_months: int = Field(..., ge=0, description="How many months the customer has been with us", examples=[12])
    is_premium_user: bool = Field(default=False, description="Is the user on a premium subscription?")


@app.post("/predict/churn", tags=["AI Inference"], status_code=status.HTTP_200_OK)
async def predict_customer_churn(payload: CustomerDataInput):
    """
    How to call this in production:
    - Send an HTTP POST request to /predict/churn
    - Content-Type header must be set to 'application/json'
    - JSON Body matches the CustomerDataInput schema.
    """
    name = payload.customer_name
    spend = payload.monthly_spend
    tenure = payload.tenure_months
    premium = payload.is_premium_user

    churn_probability = 0.15
    if spend > 100.0 and tenure < 3:
        churn_probability = 0.85
    elif premium:
        churn_probability = 0.05
        
    is_churn_risk = churn_probability > 0.5
    
    return {
        "status": "success",
        "customer": name,
        "inference_results": {
            "churn_probability": round(churn_probability, 2),
            "churn_risk_detected": is_churn_risk,
            "action_required": "Trigger retention email" if is_churn_risk else "None"
        }
    }
