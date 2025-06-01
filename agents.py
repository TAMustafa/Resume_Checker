import logfire
from pathlib import Path
from pydantic import ValidationError
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Load models and prompts
from models import JobRequirements, CVAnalysis, MatchingScore
from prompts import *

# Load environment variables
load_dotenv()

# Configure logfire logging
logfire.configure()
logfire.instrument_pydantic_ai()

# --- Agent Definitions ---
# Configure model settings with temperature=0.3 for more focused, deterministic outputs
model_settings = {
    'temperature': 0.3,  # Lower temperature for more focused, less random outputs
    'max_tokens': 2000   # Ensure we have enough tokens for detailed responses
}

job_requirements_agent = Agent(
    'openai:gpt-4o-mini',
    output_type=JobRequirements,
    system_prompt=job_requirements_prompt,
    model_settings=model_settings
)

cv_review_agent = Agent(
    'openai:gpt-4o-mini',
    output_type=CVAnalysis,
    system_prompt=cv_review_prompt,
    model_settings=model_settings
)

scoring_agent = Agent(
    'openai:gpt-4o-mini',
    output_type=MatchingScore,
    system_prompt=scoring_prompt,
    model_settings=model_settings
)

# --- Core Functions ---
async def analyze_job_vacancy(vacancy_text: str) -> JobRequirements:
    """
    Extract requirements from job vacancy text
    """
    try:
        result = await job_requirements_agent.run(
            f"Extract the job requirements and any other relevant information from the vacancy text: {vacancy_text}"
        )
        return result.output
    except ValidationError as e:
        logfire.error(f"Validation error in analyze_job_vacancy: {e}")
        raise

async def analyze_cv(pdf_path: Path) -> CVAnalysis:
    """
    Analyze CV and extract key information
    """
    global _cv_analysis_store
    
    try:
        result = await cv_review_agent.run([
            f"Analyze the CV and provide a detailed breakdown of strengths, weaknesses, and improvement recommendations.",
            BinaryContent(data=pdf_path.read_bytes(), media_type='application/pdf'),
        ])
        
        # Store the analysis in the module-level variable
        _cv_analysis_store = result.output.dict()
        
        return result.output
    except ValidationError as e:
        logfire.error(f"Validation error in analyze_cv: {e}")
        raise

async def score_cv_match(cv_analysis: CVAnalysis, job_requirements: JobRequirements) -> MatchingScore:
    """
    Score how well the CV matches the job requirements
    """
    try:
        result = await scoring_agent.run(
            f"Provide a score between 0 and 100 based on how well the CV matches the job requirements: {cv_analysis} {job_requirements}"
        )
        return result.output
    except ValidationError as e:
        logfire.error(f"Validation error in score_cv_match: {e}")
        raise

# --- FastAPI API ---
app = FastAPI()

# Serve the frontend.html at the root
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()

class VacancyRequest(BaseModel):
    vacancy_text: str

@app.post("/analyze-job-vacancy")
async def api_analyze_job_vacancy(req: VacancyRequest):
    try:
        result = await analyze_job_vacancy(req.vacancy_text)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-cv")
async def api_analyze_cv(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        contents = await file.read()
        tmp_path = Path(f"/tmp/{file.filename}")
        tmp_path.write_bytes(contents)
        result = await analyze_cv(tmp_path)
        tmp_path.unlink(missing_ok=True)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Store CV analysis in a module-level variable as a simple in-memory store
# In a production environment, consider using a proper database or cache
_cv_analysis_store = None

@app.get("/analyze-cv-summary")
async def api_analyze_cv_summary():
    """Return a summary of CV analysis without requiring job requirements"""
    if _cv_analysis_store is None:
        raise HTTPException(status_code=404, detail="No CV analysis found. Please upload a CV first.")
    return _cv_analysis_store

class ScoreRequest(BaseModel):
    cv_analysis: dict
    job_requirements: dict

@app.post("/score-cv-match")
async def api_score_cv_match(req: ScoreRequest):
    try:
        cv_obj = CVAnalysis(**req.cv_analysis)
        job_obj = JobRequirements(**req.job_requirements)
        result = await score_cv_match(cv_obj, job_obj)
        return result.model_dump() if hasattr(result, 'model_dump') else result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))