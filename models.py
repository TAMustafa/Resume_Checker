from pydantic import BaseModel, Field
from typing import List, Optional

class JobRequirements(BaseModel):
    """Represents job requirements extracted from a job posting."""
    skills: List[str] = Field(default_factory=list, description="Required skills")
    experience: str = Field(..., description="Required years/type of experience")
    qualifications: List[str] = Field(default_factory=list, description="Other qualifications or certifications")
    languages: List[str] = Field(default_factory=list, description="Required languages")
    certifications: List[str] = Field(default_factory=list, description="Required certifications")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities or duties")
    seniority_level: Optional[str] = Field(None, description="Seniority level (e.g., junior, senior, lead)")
    model_config = {'strict': True}

class CVAnalysis(BaseModel):
    """Represents the analysis of a CV."""
    skills: List[str] = Field(default_factory=list, description="Skills found in the CV")
    experience_summary: str = Field(..., description="Summary of relevant experience")
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    certifications: List[str] = Field(default_factory=list, description="Certifications listed")
    responsibilities: List[str] = Field(default_factory=list, description="Responsibilities held in previous roles")
    seniority_level: Optional[str] = Field(None, description="Seniority level inferred from CV")
    model_config = {'strict': True}

class MatchingScore(BaseModel):
    """Represents the matching score between a CV and job requirements."""
    overall_score: int = Field(..., description="Overall match score (0-100)")
    skills_match: int = Field(..., description="Skills match score (0-100)")
    experience_match: int = Field(..., description="Experience match score (0-100)")
    detailed_feedback: str = Field(..., description="Detailed feedback on the match")
    missing_requirements: List[str] = Field(default_factory=list, description="Requirements not met")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    matched_skills: List[str] = Field(default_factory=list, description="Skills that matched")
    matched_qualifications: List[str] = Field(default_factory=list, description="Qualifications/certifications that matched")
    matched_languages: List[str] = Field(default_factory=list, description="Languages that matched")
    model_config = {'strict': True}