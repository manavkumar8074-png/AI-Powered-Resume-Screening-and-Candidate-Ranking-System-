
from utils.gpt_resume_analyzer import analyze_resume_with_gpt


def main():
    resume = """
    BTech Computer Science student.
    Skills: Python, SQL, HTML, CSS.
    Project: AI-Powered Resume Screening System using Flask.
    Education: BTech in Computer Science and Engineering.
    """

    job_description = """
    We are looking for a fresher with Python, SQL,
    problem-solving, and web development skills.
    Knowledge of Flask and database management is preferred.
    """

    print("Testing Gemini Resume Analysis...")
    print("-" * 45)

    result = analyze_resume_with_gpt(resume, job_description)

    if result.get("status") == "success":
        print("\nGemini Analysis Successful")
        print("Model:", result.get("model", "Gemini"))
        print("\nResume Analysis:\n")
        print(result.get("analysis", "No analysis returned."))

    else:
        print("\nGemini Analysis Failed")
        print("Error:", result.get("error", "Unknown error"))


if __name__ == "__main__":
    main()
