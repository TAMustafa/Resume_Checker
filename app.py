import streamlit as st
import requests
import base64
from pathlib import Path
import json
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="Resume Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stTextArea>div>div>textarea {
        min-height: 200px;
    }
    .score-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .match-score {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin: 1rem 0;
    }
    .section {
        margin-bottom: 2rem;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# API URL (assuming FastAPI is running on localhost:8000)
API_URL = "http://localhost:8000"

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.job_requirements = None
    st.session_state.cv_analysis = None
    st.session_state.matching_score = None
    st.session_state.cv_analyzed = False

def analyze_job_vacancy(vacancy_text: str) -> Dict[str, Any]:
    """Send job vacancy text to the API for analysis"""
    try:
        response = requests.post(
            f"{API_URL}/analyze-job-vacancy",
            json={"vacancy_text": vacancy_text}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error analyzing job vacancy: {str(e)}")
        return None

def analyze_cv(uploaded_file) -> Dict[str, Any]:
    """Upload and analyze CV"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(
            f"{API_URL}/analyze-cv",
            files=files
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error analyzing CV: {str(e)}")
        return None

def get_matching_score(cv_analysis: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Get matching score between CV and job requirements"""
    try:
        response = requests.post(
            f"{API_URL}/score-cv-match",
            json={
                "cv_analysis": cv_analysis,
                "job_requirements": job_requirements
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error getting matching score: {str(e)}")
        return None

def display_analysis():
    """Display the analysis results"""
    if st.session_state.matching_score:
        score = st.session_state.matching_score
        
        # Overall score card
        with st.container():
            st.markdown("## 📊 Match Analysis")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### Overall Match Score")
                st.markdown(f"<div class='match-score'>{score.get('overall_score', 0)}/100</div>", unsafe_allow_html=True)
                
                # Score breakdown
                st.metric("Skills Match", f"{score.get('skills_match', 0)}/100")
                st.metric("Experience Match", f"{score.get('experience_match', 0)}/100")
                st.metric("Education Match", f"{score.get('education_match', 0)}/100")
            
            with col2:
                st.markdown("### Detailed Feedback")
                st.write(score.get('detailed_feedback', 'No feedback available.'))
        
        # Matched skills and qualifications
        if score.get('matched_skills') or score.get('matched_qualifications'):
            with st.expander("✅ Matched Skills & Qualifications", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    if score.get('matched_skills'):
                        st.markdown("#### Skills Matched")
                        for skill in score.get('matched_skills', []):
                            st.markdown(f"- {skill}")
                with cols[1]:
                    if score.get('matched_qualifications'):
                        st.markdown("#### Qualifications Matched")
                        for qual in score.get('matched_qualifications', []):
                            st.markdown(f"- {qual}")
        
        # Missing requirements
        if score.get('missing_requirements'):
            with st.expander("❌ Missing Requirements", expanded=True):
                st.markdown("The following job requirements were not found in your CV:")
                for req in score.get('missing_requirements', []):
                    st.markdown(f"- {req}")
        
        # Improvement suggestions
        if score.get('improvement_suggestions'):
            with st.expander("💡 Suggestions for Improvement", expanded=True):
                for suggestion in score.get('improvement_suggestions', []):
                    st.markdown(f"- {suggestion}")

# Main app
def display_cv_analysis():
    """Display CV analysis results"""
    if 'cv_analysis' not in st.session_state or st.session_state.cv_analysis is None:
        st.warning("No CV analysis available. Please upload and analyze a CV first.")
        return
    
    cv_analysis = st.session_state.cv_analysis
    
    # Check if cv_analysis is a dictionary and has the expected structure
    if not isinstance(cv_analysis, dict):
        st.error("Invalid CV analysis format. Please try analyzing your CV again.")
        return
    
    st.markdown("## 📄 CV Analysis Results")
    
    with st.expander("View Full CV Analysis", expanded=True):
        # Key Skills
        if cv_analysis.get('key_skills'):
            st.markdown("### Key Skills")
            cols = st.columns(3)
            for i, skill in enumerate(cv_analysis['key_skills']):
                with cols[i % 3]:
                    st.markdown(f"- {skill}")
        
        # Experience Summary
        if cv_analysis.get('experience_summary'):
            st.markdown("### Experience Summary")
            st.write(cv_analysis['experience_summary'])
        
        # Education
        if cv_analysis.get('education'):
            st.markdown("### Education")
            st.write(cv_analysis['education'])
        
        # Strengths
        if cv_analysis.get('strengths'):
            st.markdown("### Strengths")
            for strength in cv_analysis['strengths']:
                st.markdown(f"- {strength}")
        
        # Recommendations
        if cv_analysis.get('recommendations'):
            st.markdown("### Recommendations")
            for rec in cv_analysis['recommendations']:
                st.markdown(f"- {rec}")

def main():
    st.title("📄 Resume Checker")
    st.markdown("Upload your CV to get started. You can also add a job description for a detailed match analysis.")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["CV Analysis", "Job Match"])
    
    with tab1:
        st.markdown("### 1. Upload Your CV (PDF)")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="cv_uploader")
        
        # Disable the Analyze CV button if no file is uploaded
        if st.button("Analyze CV", disabled=uploaded_file is None):
            if uploaded_file is not None:
                with st.spinner("Analyzing CV..."):
                    try:
                        # Analyze CV
                        cv_analysis = analyze_cv(uploaded_file)
                        if cv_analysis and isinstance(cv_analysis, dict):
                            st.session_state.cv_analysis = cv_analysis
                            st.session_state.cv_analyzed = True
                            st.success("CV analyzed successfully!")
                            # Show the analysis results
                            st.rerun()
                        else:
                            st.error("Failed to analyze CV. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred while analyzing the CV: {str(e)}")
            else:
                st.warning("Please upload a PDF file")
        
        # Display CV analysis if available
        display_cv_analysis()
    
    with tab2:
        st.markdown("### 2. Optional: Add Job Description for Matching")
        job_text = st.text_area(
            "Paste the job description here (optional)",
            placeholder="Paste the job description to see how well your CV matches...",
            height=200,
            key="job_text"
        )
        
        if st.button("Analyze Job Match"):
            if not st.session_state.get('cv_analyzed') or 'cv_analysis' not in st.session_state:
                st.warning("Please analyze your CV first")
            elif not job_text.strip():
                st.warning("Please enter a job description")
            else:
                with st.spinner("Analyzing job requirements and calculating match..."):
                    try:
                        # Analyze job requirements
                        job_req = analyze_job_vacancy(job_text)
                        if job_req and isinstance(job_req, dict):
                            st.session_state.job_requirements = job_req
                            
                            # Get matching score
                            matching_score = get_matching_score(
                                st.session_state.cv_analysis,
                                job_req
                            )
                            
                            if matching_score and isinstance(matching_score, dict):
                                st.session_state.matching_score = matching_score
                                st.success("Job match analysis complete!")
                                st.rerun()
                            else:
                                st.error("Failed to calculate matching score. Please try again.")
                        else:
                            st.error("Failed to analyze job requirements. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred during job matching: {str(e)}")
    
    # Display results if available
    if st.session_state.matching_score:
        st.markdown("---")
        display_analysis()

if __name__ == "__main__":
    main()
