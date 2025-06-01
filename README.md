# Resume Checker Application

A powerful AI-driven application that analyzes resumes and matches them against job descriptions. The application provides detailed insights into how well a candidate's qualifications match job requirements and offers improvement suggestions.

## Features

- **CV Analysis**: Upload and analyze PDF resumes to extract key skills, experience, and qualifications
- **Job Description Analysis**: Parse job descriptions to extract key requirements
- **Matching Score**: Get a detailed matching score between a CV and job description
- **Improvement Suggestions**: Receive actionable recommendations to improve your resume
- **User-Friendly Interface**: Intuitive web interface built with Streamlit

## Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- OpenAI API key (for AI-powered analysis)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ResumeChecker.git
   cd ResumeChecker
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

The application consists of two main components:

### 1. Backend API (FastAPI)

Run the FastAPI server in a terminal window:

```bash
uvicorn agents:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Frontend (Streamlit)

In a new terminal window (with the virtual environment activated), run:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage Guide

### 1. CV Analysis

1. **Upload Your CV**
   - Click on the "Choose a PDF file" button to upload your resume
   - The "Analyze CV" button will become active once a file is selected
   - Click "Analyze CV" to process your resume

2. **View Analysis Results**
   - The system will display your key skills, experience summary, and education
   - Review the analysis for accuracy
   - Check the recommendations for improving your resume

### 2. Job Match Analysis (Optional)

1. **Switch to the "Job Match" Tab**
   - Click on the "Job Match" tab at the top of the page

2. **Enter Job Description**
   - Paste the job description in the text area
   - Click "Analyze Job Match" to compare your CV with the job requirements

3. **Review Matching Results**
   - View your overall match score (0-100)
   - See detailed breakdown by category (skills, experience, education)
   - Review matched and missing requirements
   - Get personalized improvement suggestions

## API Endpoints

The backend provides the following RESTful endpoints:

- `POST /analyze-job-vacancy`: Analyze job description
  ```json
  {
    "vacancy_text": "Job description text here..."
  }
  ```

- `POST /analyze-cv`: Analyze uploaded CV (PDF)
  - Content-Type: multipart/form-data
  - File field: file (PDF)

- `POST /score-cv-match`: Get matching score between CV and job requirements
  ```json
  {
    "cv_analysis": { /* CV analysis object */ },
    "job_requirements": { /* Job requirements object */ }
  }
  ```

## Project Structure

```
ResumeChecker/
├── .env                    # Environment variables
├── app.py                  # Streamlit frontend
├── agents.py               # FastAPI backend and AI agents
├── models.py               # Pydantic models
├── prompts.py              # AI prompt templates
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Customization

### Updating AI Prompts

You can modify the AI behavior by editing the prompts in `prompts.py`. The main prompts are:

- `job_requirements_prompt`: For extracting job requirements
- `cv_review_prompt`: For analyzing CVs
- `scoring_prompt`: For calculating match scores

### Styling

To modify the application's appearance, edit the CSS in the `st.markdown` section at the top of `app.py`.

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure the FastAPI server is running
   - Check that the API URL in `app.py` matches your FastAPI server's address

2. **Missing Dependencies**
   - Run `pip install -e .` to ensure all dependencies are installed
   - Check that you're using Python 3.12 or higher

3. **PDF Parsing Issues**
   - Ensure the uploaded file is a valid PDF
   - Try with a different PDF file to rule out file corruption

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Streamlit](https://streamlit.io/)
- Powered by OpenAI's GPT models
- Icons by [Material Design Icons](https://material.io/resources/icons/)
