from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI(
    title="AI HR-Tech Production Pipeline",
    description="HR tech analysis each resume for carefully shortlisted candidate.",
    version="1.0.0",

            )

# 1. WRITE YOUR PYDANTIC MODEL HERE
class ResumeInput(BaseModel):
    candidate_name: Annotated[str, Field(min_length=3, description="Name of Candidate")]
    years_of_experience: Annotated[int, Field(ge=0, description="Work experience of candidate")]
    skills_list: Annotated[list[str], Field(examples=[['python', 'machine learning', 'deep learning']])]
    current_salary: Annotated[float, Field(gt=0.0, description='Leave time or if you still there your current salary.')]
    is_remote_prefered: Annotated[bool, Field(default=True, description="Would you like to work in remotely")]

class ResumeResponse(BaseModel):
    status:str = Field(description=('Status processing'))
    candidate: str = Field(description=("Name filtered safely"))
    is_shortlisted: bool = Field(description=("Final Evaluating decsion flag"))
    new_estimated_salary: float = Field(description="AI new shortlist salary calculation.")

# 2. WRITE YOUR POST ROUTE HANDLER HERE
@app.post("/ai/shortlist",
        status_code=status.HTTP_201_CREATED,
        tags=["HR AI Analytics"],
        response_model=ResumeResponse
        )
async def shortlist_candidate(payload: ResumeInput):
    # Write your logic here
    # 1. Extract data from payload
    # 2. Check conditions for skills and experience
    # 3. Calculate salary estimation
    # 4. Return the structured dict response
    
    name = payload.candidate_name
    stack_list = payload.skills_list
    has_python = 'python' in [s.lower() for s in stack_list]
    has_fastapi = 'fastapi' in [s.lower() for s in stack_list]
    experience = payload.years_of_experience
    new_estimated_salary = payload.current_salary
    is_shortlisted = False
    if has_python and has_fastapi and experience>=2:
        is_shortlisted = True

    if is_shortlisted:
        new_estimated_salary = new_estimated_salary * 1.3

    return {
    "status": "processed",
    "candidate": name,
    "is_shortlisted": is_shortlisted,
    "new_estimated_salary": round(new_estimated_salary, 2),
    "message": "Congratulations! You are shortlisted for the interview." if is_shortlisted else "Thank you for applying. We will keep your resume on file.",
    "internal_gpu_inference_latency" : "14ms",
    "database_transaction_id": "tx_99834211_applied_ai",
    "raw_server_logs_dump": "Processing thread execution token matches success"
}

