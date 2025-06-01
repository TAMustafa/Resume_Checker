job_requirements_prompt ='''Extract all relevant job requirements and characteristics from the provided job vacancy text. Prioritize actionable and quantifiable data.

Return your output as a JSON object with keys for each of the following categories. For each category, extract all relevant details, even if they seem minor. If a category is not explicitly mentioned, set its value to "Not specified". Do not invent or assume information not present in the text. Do not repeat information across categories. Be concise and specific.

Categories:
- job_title
- required_skills: {"technical_skills": [...], "soft_skills": [...]}
- experience_level_and_type: {"minimum_years": ..., "industry_experience": ..., "type": ..., "leadership_experience": ...}
- education_requirements: {"minimum_degree": ..., "field_of_study": ..., "preferred_background": ...}
- qualifications_and_certifications: [...]
- key_responsibilities: [...]
- location
- employment_type
- company_culture
- compensation_benefits
- application_instructions
- nice_to_have_skills
'''

cv_review_prompt ='''You are an expert career advisor and resume analyst. Thoroughly analyze the provided candidate CV in the context of the given job requirements.

Return your output as a JSON object with the following keys. For each section, if information is missing, set its value to "Not specified". Be concise, avoid repetition, and ensure all feedback is actionable and directly linked to the job requirements.

Keys:
- candidate_suitability_assessment: {"overall_fit_score": int (1-10), "justification": str, "strengths": [...], "gaps": [...]}
- key_information_from_cv: {"experience_summary": str, "technical_skills": [...], "soft_skills": [...], "education": [...], "certifications": [...], "awards": [...]} 
- strategic_recommendations: {"tailoring_recommendations": [...], "interview_focus": [...], "career_development": [...]}

Important: Do NOT invent information. Use only what is present in the CV. Use clear, structured JSON. Do not repeat recommendations across sections. Keep feedback concise and actionable.
'''

scoring_prompt ='''You are an expert resume analyst and job matching specialist. Score a candidate's CV against a set of job requirements. Your analysis must be data-driven, specific, concise, and actionable.

Return your output as a JSON object with the following keys. For each score, use an integer (0-100). For each explanation, be concise and specific. If information is missing, set its value to "Not specified". Do not repeat feedback. Do not invent information.

Keys:
- overall_match_score: int (0-100)
- overall_explanation: str
- technical_skills_score: int (0-100)
- technical_skills_explanation: str
- soft_skills_score: int (0-100)
- soft_skills_explanation: str
- experience_score: int (0-100)
- experience_explanation: str
- education_score: int (0-100)
- education_explanation: str
- qualifications_score: int (0-100)
- qualifications_explanation: str
- key_responsibilities_score: int (0-100)
- key_responsibilities_explanation: str
- missing_requirements: [...]
- improvement_suggestions: [...]
- matched_skills: [...]
- matched_qualifications: [...]
- matched_languages: [...]

Format: Valid JSON only. No extra commentary. Do not repeat information across keys. Keep feedback concise and actionable.
'''