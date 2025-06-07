import streamlit as st
import requests
from typing import Dict, Any
from streamlit.runtime.caching import cache_data
import os

# Page configuration
st.set_page_config(
    page_title="Resume Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def analyze_cv(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Upload and analyze CV"""
    files = {"file": (filename, file_bytes, "application/pdf")}
    response = requests.post(
        f"{API_URL}/analyze-cv",
        files=files,
        timeout=60,
    )
    if response.status_code == 200:
        return response.json()
    else:
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

# --- Caching for performance ---
@cache_data(show_spinner=False)
def cached_analyze_cv(file_bytes: bytes, filename: str):
    return analyze_cv(file_bytes, filename)

@cache_data(show_spinner=False)
def cached_analyze_job_vacancy(job_text):
    return analyze_job_vacancy(job_text)

@cache_data(show_spinner=False)
def cached_get_matching_score(cv_analysis, job_requirements):
    return get_matching_score(cv_analysis, job_requirements)

def display_analysis():
    """Display the analysis results"""
    if st.session_state.matching_score:
        score = st.session_state.matching_score
        
        # Overall score card
        with st.container():
            st.header("Match Analysis")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Overall Match Score")
                score_value = score.get('overall_score', 0)
                # Determine color and icon
                if score_value < 70:
                    color = 'orange'
                    icon = '⚠️'
                elif 70 <= score_value < 85:
                    color = 'green'
                    icon = '✅'
                else:
                    color = 'blue'
                    icon = '🌟'
                st.markdown(f"<span style='font-size:2.5rem;font-weight:bold;color:{color};'>{icon} {score_value}/100</span>", unsafe_allow_html=True)
                st.metric("Overall Match Score", f"{score_value}/100")
                
                # Score breakdown
                st.metric("Skills Match", f"{score.get('skills_match', 0)}/100")
                st.metric("Experience Match", f"{score.get('experience_match', 0)}/100")
                st.metric("Education Match", f"{score.get('education_match', 0)}/100")
            
            with col2:
                st.subheader("Detailed Feedback")
                st.write(score.get('detailed_feedback', 'No feedback available.'))
        
        # Matched skills and qualifications
        if score.get('matched_skills') or score.get('matched_qualifications'):
            with st.expander("Matched Skills & Qualifications", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    if score.get('matched_skills'):
                        st.subheader("Skills Matched")
                        st.dataframe({"Skills": score.get('matched_skills', [])})
                with cols[1]:
                    if score.get('matched_qualifications'):
                        st.subheader("Qualifications Matched")
                        st.dataframe({"Qualifications": score.get('matched_qualifications', [])})
        
        # Missing requirements
        if score.get('missing_requirements'):
            with st.expander("Missing Requirements", expanded=True):
                st.subheader("The following job requirements were not found in your CV:")
                st.dataframe({"Missing Requirements": score.get('missing_requirements', [])})
        
        # Improvement suggestions
        if score.get('improvement_suggestions'):
            with st.expander("Suggestions for Improvement", expanded=True):
                for suggestion in score.get('improvement_suggestions', []):
                    st.write(suggestion)
        
        # Download analysis results
        if score:
            st.download_button(
                label="Download Analysis as JSON",
                data=str(score),
                file_name="analysis_result.json",
                mime="application/json"
            )

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
    
    st.header("CV Analysis Results")
    
    # Main details in expander
    with st.expander("View Full CV Analysis", expanded=True):
        # Key Skills
        if cv_analysis.get('key_skills'):
            st.subheader("Key Skills")
            st.dataframe({"Key Skills": cv_analysis['key_skills']})
        # Experience Summary
        if cv_analysis.get('experience_summary'):
            st.subheader("Experience Summary")
            st.write(cv_analysis['experience_summary'])
        # Education
        if cv_analysis.get('education'):
            st.subheader("Education")
            st.write(cv_analysis['education'])
        # Strengths
        if cv_analysis.get('strengths'):
            st.subheader("Strengths")
            for strength in cv_analysis['strengths']:
                st.write(strength)
        # Recommendations
        if cv_analysis.get('recommendations'):
            st.subheader("Recommendations")
            for rec in cv_analysis['recommendations']:
                st.write(rec)

    # Raw JSON analysis output in a separate expander (not nested)
    with st.expander("View Raw Analysis JSON"):
        st.json(cv_analysis)

# --- Persistent CV storage directory ---
CV_DIR = "uploaded_cvs"
os.makedirs(CV_DIR, exist_ok=True)

def list_saved_cvs():
    files = [f for f in os.listdir(CV_DIR) if f.lower().endswith(".pdf")]
    return files

def save_uploaded_cv(uploaded_file):
    filename = uploaded_file.name
    # Ensure unique filename
    base, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(os.path.join(CV_DIR, filename)):
        filename = f"{base}_{i}{ext}"
        i += 1
    with open(os.path.join(CV_DIR, filename), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filename

def load_cv_file(filename):
    with open(os.path.join(CV_DIR, filename), "rb") as f:
        return f.read()

def main():
    # --- Sidebar with app info and instructions ---
    st.sidebar.title("Resume Checker")
    st.sidebar.info("""
    Upload your CV and optionally a job description to analyze your fit for a role. 
    - Use the **CV Analysis** tab to get a breakdown of your skills and experience.
    - Use the **Job Match** tab to see how your CV matches a specific job description.

    All analysis is local and sent securely to your FastAPI backend running at localhost:8000.
    """)
    
    # --- Add st.info at the top for user guidance ---
    st.info("Upload your CV and optionally a job description to analyze your fit for a role.")
    
    st.title("Resume Checker")
    st.write("Upload your CV to get started. You can also add a job description for a detailed match analysis.")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["CV Analysis", "Job Match"])
    
    with tab1:
        st.subheader("1. Upload Your CV (PDF)")
        saved_cvs = list_saved_cvs()
        selected_cv = None
        if saved_cvs:
            selected_cv = st.selectbox("Or select a previously uploaded CV:", ["Upload new CV"] + saved_cvs)
        else:
            st.write("No previously uploaded CVs found.")
            selected_cv = "Upload new CV"

        file_bytes = None
        filename = None
        if selected_cv == "Upload new CV":
            uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="cv_uploader")
            if uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                filename = uploaded_file.name
        else:
            filename = selected_cv
            file_bytes = load_cv_file(filename)

        analyze_cv_btn = st.button("Analyze CV", disabled=(file_bytes is None or filename is None))
        if analyze_cv_btn:
            if file_bytes is not None and filename is not None:
                # If it's a new upload, save it
                if selected_cv == "Upload new CV" and uploaded_file is not None:
                    saved_filename = save_uploaded_cv(uploaded_file)
                    st.success(f"CV saved as {saved_filename}")
                with st.spinner("Analyzing CV..."):
                    cv_analysis = cached_analyze_cv(file_bytes, filename)
                    if cv_analysis and isinstance(cv_analysis, dict):
                        st.session_state.cv_analysis = cv_analysis
                        st.session_state.cv_analyzed = True
                        st.success("CV analyzed successfully!")
                        st.toast("CV analysis complete!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Failed to analyze CV. Please try again.")
            else:
                st.warning("Please upload a PDF file or select one from the list.")

        display_cv_analysis()

    with tab2:
        st.subheader("2. Optional: Add Job Description for Matching")
        job_text = st.text_area(
            "Paste the job description here (optional)",
            placeholder="Paste the job description to see how well your CV matches...",
            height=200,
            key="job_text"
        )

        analyze_job_btn = st.button("Analyze Job Match")
        if analyze_job_btn:
            if not st.session_state.get('cv_analyzed') or 'cv_analysis' not in st.session_state:
                st.warning("Please analyze your CV first")
            elif not job_text.strip():
                st.warning("Please enter a job description")
            else:
                with st.spinner("Analyzing job requirements and calculating match..."):
                    job_req = cached_analyze_job_vacancy(job_text)
                    if job_req and isinstance(job_req, dict):
                        st.session_state.job_requirements = job_req
                        matching_score = cached_get_matching_score(
                            st.session_state.cv_analysis,
                            job_req
                        )
                        if matching_score and isinstance(matching_score, dict):
                            st.session_state.matching_score = matching_score
                            st.success("Job match analysis complete!")
                            st.toast("Job match complete!", icon="🎯")
                            st.rerun()
                        else:
                            st.error("Failed to calculate matching score. Please try again.")
                    else:
                        st.error("Failed to analyze job requirements. Please try again.")

    # Display results if available
    if st.session_state.matching_score:
        st.write("---")
        display_analysis()

if __name__ == "__main__":
    main()
