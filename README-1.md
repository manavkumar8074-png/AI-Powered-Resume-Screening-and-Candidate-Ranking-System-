# AI-Powered Resume Screening and Candidate Ranking System

An AI-assisted recruitment support application that compares candidate resumes with a job description, evaluates job-related qualifications and evidence, and ranks applicants using an explainable six-factor scoring model. The application also provides a Gemini-powered supplementary resume analysis to help recruiters review candidate strengths and gaps.

> **Note:** The screening result is a recommendation for human review, not an automatic hiring decision.

## Project Overview

Recruiters often need to review many resumes for a single opening. Manual screening takes time and can lead to inconsistent comparisons. This project provides a web interface for uploading resumes, analyzing job requirements, checking candidate qualifications, calculating weighted scores, and displaying ranked candidates with supporting evidence.

## Features

- Upload and analyze one or multiple resumes.
- Accept PDF, DOCX, DOC, TXT, JPG, JPEG, and PNG files; scanned-image extraction requires OCR to be configured.
- Extract and normalize resume text.
- Analyze job descriptions to identify required and preferred skills.
- Evaluate technical, specialized, preferred, and soft skills.
- Examine contextual evidence and proficiency indicators for identified skills.
- Compare education details with job-description requirements.
- Evaluate project relevance and implementation evidence.
- Generate weighted candidate scores and rankings.
- Show matched skills, missing skills, evidence summaries, and screening recommendations.
- Display supplementary Gemini API analysis of a resume against the job description.

## Technology Stack

| Area | Technologies documented in the project report |
| --- | --- |
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| NLP and text processing | spaCy, NLTK |
| Document extraction | PyPDF2, pdfplumber, python-docx |
| Image and OCR support | Pillow, pytesseract (when configured) |
| Similarity and numerical processing | Scikit-learn, NumPy |
| Data handling | Pandas |
| Generative analysis | Gemini API |
| Version control | Git, GitHub |

The technologies above are documented in the report; confirm the dependencies in the current project environment before deployment. Database configuration, if any, depends on the deployed version.

## Six-Factor Candidate Scoring

| Scoring factor | Weight |
| --- | ---: |
| Technical Skills | 35% |
| Specialized Skills | 25% |
| Preferred Skills | 10% |
| Soft Skills | 5% |
| Education | 15% |
| Project Relevance | 10% |
| **Total** | **100%** |

The overall score is calculated as:

```text
Overall Score = 0.35 × Technical + 0.25 × Specialized
              + 0.10 × Preferred + 0.05 × Soft
              + 0.15 × Education + 0.10 × Projects
```

Each component is scored on a 0–100 scale.

| Overall score | Recommendation |
| --- | --- |
| 80% or above | Strong Match |
| 65% to below 80% | Good Match |
| 50% to below 65% | Moderate Match |
| Below 50% | Low Match |

The application also produces a separate screening decision using a 65% overall-score threshold. Similarity and evidence scores are displayed as additional information and should not be confused with measured model accuracy.

## How the System Works

1. Enter or provide a job description.
2. Upload candidate resumes.
3. Extract and preprocess resume text.
4. Identify job requirements and candidate skills.
5. Evaluate education, skill evidence, and project relevance.
6. Calculate six weighted component scores.
7. Rank candidates and display individual analysis pages.
8. Review strengths, gaps, screening decision, and optional Gemini analysis.
9. Make the final recruitment decision through human review.

## Project Structure

The development screenshots show a structure similar to:

```text
AI_Resume_screening/
├── ai.py
├── .env
├── templates/
│   ├── index.html
│   └── candidate.html
├── uploads/
└── utils/
    ├── evidence_verifier.py
    ├── gpt_resume_analyzer.py
    ├── jd_analyzer.py
    ├── pdf_extractor.py
    ├── resume_analyzer.py
    ├── resume_extractor.py
    ├── resumematcher.py
    ├── score_calculator.py
    ├── skill_extractor.py
    ├── test_gpt.py
    └── text_preprocessor.py
```

The final repository may contain additional files. Some report versions refer to `app.py` for Flask routing; use the actual entry-point filename in your repository.

## Installation and Running Locally

### Prerequisites

- Python 3.10 or newer, as specified in the project report
- pip
- A Gemini API key if using the Gemini analysis feature
- OCR dependencies if testing scanned resumes

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the placeholder URL and folder name with your actual public repository details.

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If the repository contains a verified `requirements.txt`:

```bash
pip install -r requirements.txt
```

Generate this file from the working environment before publishing if it does not yet exist. Do not assume that every library listed in the report is required by the current code.

### 4. Configure environment variables

Create a local `.env` file and add the Gemini API credential using the **exact variable name expected by your code**. For example, if your implementation reads `GEMINI_API_KEY`:

```dotenv
GEMINI_API_KEY=your_api_key_here
```

The exact variable name and model configuration should be checked in `utils/gpt_resume_analyzer.py` or the relevant integration module.

### 5. Start the application

The screenshot of the project folder shows `ai.py` at the root. If it is the Flask entry point, run:

```bash
python ai.py
```

If the actual repository uses `app.py` as the entry point, run `python app.py` instead. Open the local URL printed in the terminal.

## Example Candidate Analysis

A captured demonstration screen displays:

| Metric | Demonstration output |
| --- | --- |
| Candidate rank | #1 |
| Overall score | 83.25% |
| Recommendation | Strong Match |
| Evidence score | 18.46% |
| Resume similarity | 3.36% |
| Project relevance | Strong |
| Screening decision | Suitable for the Job |

These values are **from one demonstration**, not an accuracy benchmark or a general performance claim. The example also illustrates why the recruiter should inspect evidence and missing requirements rather than relying on the overall score alone.

## Screenshots

To display screenshots on GitHub, create a `screenshots/` directory, copy suitable images into it, and add links such as:

```markdown
![Candidate Analysis](screenshots/candidate-analysis.png)
![Score Breakdown](screenshots/score-breakdown.png)
![Gemini Resume Analysis](screenshots/gemini-analysis.png)
```

Only add those links after placing the files at the corresponding paths. Remove or anonymize personal information in screenshots before publishing.

## Security and Responsible Use

- Do not commit `.env`, API keys, credentials, or private candidate resumes.
- Exclude `.venv/`, `__pycache__/`, and uploaded resume files from Git.
- Validate uploaded file types and sizes.
- Review ambiguous education or skill evidence manually.
- Evaluate fairness and bias before using screening recommendations in real recruitment.
- Treat Gemini output as supporting analysis rather than independently verified facts.

A suggested `.gitignore` includes:

```gitignore
.env
.venv/
__pycache__/
*.pyc
uploads/*
!uploads/.gitkeep
```

## SDG Alignment

**SDG 8 – Decent Work and Economic Growth**

This project uses Artificial Intelligence to automate resume screening and candidate ranking, helping organizations recruit suitable candidates efficiently. It reduces manual effort, speeds up the hiring process, and supports fair employment opportunities through intelligent recruitment.

## Project Team

**Presidency University, Bengaluru**  
Presidency School of Artificial Intelligence & Advanced Computing  
B.Tech – Computer Science and Engineering (AI & ML)

| Student | USN |
| --- | --- |
| Kasa Manav Kumar Reddy | 20231CAI0009 |
| Mooli Somasekhar Reddy | 20241CAI3004 |
| Bikkina Pawan Prabhas | 20231CAI0049 |
| Nitesh Virendra Koulagikar | 20241CAI3008 |

**Project Guide:** Dr. Vijaya Kumar A, Professor, PSAIAC, Presidency University.

## Future Scope

Potential improvements include stronger synonym and semantic matching, broader skill taxonomies, multilingual resume support, more robust OCR, systematic bias evaluation, larger-scale testing, and improved privacy controls.

## License

No license has been specified in the project materials. Add a license file only after the project team and guide decide how the repository may be reused.
