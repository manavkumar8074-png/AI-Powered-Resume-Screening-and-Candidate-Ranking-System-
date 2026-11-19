
import re


def normalize_text(text):
    text = str(text or "").lower()

    replacements = {
        "bachelor of technology": "b tech",
        "bachelor of engineering": "b e",
        "master of technology": "m tech",
        "master of engineering": "m e",
        "b.tech": "b tech",
        "b.e.": "b e",
        "m.tech": "m tech",
        "m.e.": "m e",
        "b.sc.": "b sc",
        "m.sc.": "m sc",
        "b.com.": "b com",
        "m.com.": "m com",
        "bachelor's": "bachelor",
        "bachelors": "bachelor",
        "master's": "master",
        "masters": "master",
        "&": " and "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9.+/\s-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_items(value):
    if isinstance(value, str):
        value = [value]

    if not isinstance(value, (list, tuple, set)):
        return set()

    return {
        normalize_text(item)
        for item in value
        if normalize_text(item)
    }


def get_degree_level(degree):
    degree = normalize_text(degree)

    bachelors_degrees = {
        "b tech",
        "b e",
        "b sc",
        "b com",
        "bca",
        "bba",
        "bachelor",
        "bachelor degree",
        "bachelors degree",
        "undergraduate"
    }

    masters_degrees = {
        "m tech",
        "m e",
        "m sc",
        "m com",
        "mca",
        "mba",
        "master",
        "master degree",
        "masters degree",
        "postgraduate"
    }

    if degree in bachelors_degrees:
        return "bachelor"

    if degree in masters_degrees:
        return "master"

    if degree in {"ph d", "ph.d", "doctorate", "doctoral degree"}:
        return "doctorate"

    if degree == "diploma":
        return "diploma"

    if degree in {"high school diploma", "high school"}:
        return "high_school"

    return degree


def extract_resume_education(resume_text):
    text = normalize_text(resume_text)

    education = {
        "degree": [],
        "degrees": [],
        "fields": [],
        "cgpa": None,
        "backlogs": "Not mentioned"
    }

    degree_patterns = {
        "B.Tech": [
            r"\bb\s*\.?\s*tech\b",
            r"\bbachelor of technology\b"
        ],
        "B.E": [
            r"\bb\s*\.?\s*e\b",
            r"\bbachelor of engineering\b"
        ],
        "M.Tech": [
            r"\bm\s*\.?\s*tech\b",
            r"\bmaster of technology\b"
        ],
        "M.E": [
            r"\bm\s*\.?\s*e\b",
            r"\bmaster of engineering\b"
        ],
        "BCA": [
            r"\bbca\b",
            r"\bbachelor of computer applications\b"
        ],
        "MCA": [
            r"\bmca\b",
            r"\bmaster of computer applications\b"
        ],
        "B.Sc": [
            r"\bb\s*\.?\s*sc\b",
            r"\bbachelor of science\b"
        ],
        "M.Sc": [
            r"\bm\s*\.?\s*sc\b",
            r"\bmaster of science\b"
        ],
        "B.Com": [
            r"\bb\s*\.?\s*com\b",
            r"\bbachelor of commerce\b"
        ],
        "M.Com": [
            r"\bm\s*\.?\s*com\b",
            r"\bmaster of commerce\b"
        ],
        "BBA": [
            r"\bbba\b",
            r"\bbachelor of business administration\b"
        ],
        "MBA": [
            r"\bmba\b",
            r"\bmaster of business administration\b"
        ],
        "Ph.D.": [
            r"\bph\s*\.?\s*d\b",
            r"\bdoctorate\b"
        ],
        "Diploma": [
            r"\bdiploma\b"
        ],
        "Associate's degree": [
            r"\bassociate(?:s)? degree\b"
        ],
        "High school diploma": [
            r"\bhigh school diploma\b"
        ]
    }

    for degree, patterns in degree_patterns.items():
        if any(re.search(pattern, text) for pattern in patterns):
            education["degree"].append(degree)

    education["degrees"] = list(education["degree"])

    field_patterns = {
        "Computer Science": [
            r"\bcomputer science and engineering\b",
            r"\bcomputer science engineering\b",
            r"\bcomputer science\b",
            r"\bcse\b"
        ],
        "Artificial Intelligence and Machine Learning": [
            r"\bartificial intelligence and machine learning\b",
            r"\bai and ml\b",
            r"\bai ml\b",
            r"\baiml\b",
            r"\bai/ml\b"
        ],
        "Artificial Intelligence": [
            r"\bartificial intelligence\b"
        ],
        "Machine Learning": [
            r"\bmachine learning\b"
        ],
        "Information Technology": [
            r"\binformation technology\b"
        ],
        "Electrical and Electronics Engineering": [
            r"\belectrical and electronics engineering\b",
            r"\belectrical and electronics\b",
            r"\beee\b"
        ],
        "Electronics and Communication Engineering": [
            r"\belectronics and communication engineering\b",
            r"\belectronics and communication\b",
            r"\bece\b"
        ],
        "Mechanical Engineering": [
            r"\bmechanical engineering\b"
        ],
        "Civil Engineering": [
            r"\bcivil engineering\b"
        ],
        "Data Science": [
            r"\bdata science\b"
        ],
        "Business Administration": [
            r"\bbusiness administration\b"
        ],
        "Commerce": [
            r"\bcommerce\b"
        ],
        "Mathematics": [
            r"\bmathematics\b"
        ],
        "Physics": [
            r"\bphysics\b"
        ],
        "Chemistry": [
            r"\bchemistry\b"
        ]
    }

    for field_name, patterns in field_patterns.items():
        if any(re.search(pattern, text) for pattern in patterns):
            education["fields"].append(field_name)

    cgpa_patterns = [
        r"\b(?:cgpa|cpi)\s*[:=]?\s*(\d{1,2}(?:\.\d+)?)\s*(?:/\s*10)?",
        r"\b(?:gpa|spi)\s*[:=]?\s*(\d{1,2}(?:\.\d+)?)\s*(?:/\s*10)?",
        r"\b(?:cgpa|gpa)\s+(?:is|of)\s*(\d{1,2}(?:\.\d+)?)"
    ]

    for pattern in cgpa_patterns:
        match = re.search(pattern, text)

        if match:
            try:
                value = float(match.group(1))

                if 0 <= value <= 10:
                    education["cgpa"] = value
                    break
            except ValueError:
                continue

    backlog_patterns = [
        r"\b(?:active|current|standing)\s+backlogs?\s*[:=]?\s*(\d+)\b",
        r"\bbacklogs?\s*[:=]?\s*(\d+)\b",
        r"\barrears?\s*[:=]?\s*(\d+)\b"
    ]

    for pattern in backlog_patterns:
        backlog_match = re.search(pattern, text)

        if backlog_match:
            education["backlogs"] = int(backlog_match.group(1))
            break

    return education


def calculate_education_score(jd_requirements, resume_education):
    jd_requirements = jd_requirements or {}
    resume_education = resume_education or {}

    checks = []

    required_degrees = normalize_items(
        jd_requirements.get("degrees", [])
    )

    resume_degrees = normalize_items(
        resume_education.get("degrees", [])
    )

    if not resume_degrees:
        resume_degrees = normalize_items(
            resume_education.get("degree", [])
        )

    required_fields = normalize_items(
        jd_requirements.get("fields", [])
    )

    resume_fields = normalize_items(
        resume_education.get("fields", [])
    )

    broad_graduation = bool(
        jd_requirements.get("broad_graduation", False)
    )

    if broad_graduation:
        acceptable_degrees = {
            degree for degree in resume_degrees
            if get_degree_level(degree) in {
                "bachelor",
                "master",
                "doctorate"
            }
        }

        checks.append({
            "requirement": "Broad graduation requirement",
            "required": "Any bachelor's degree or higher",
            "resume_value": sorted(resume_degrees),
            "matched": bool(acceptable_degrees),
            "score": 100 if acceptable_degrees else 0
        })

    elif required_degrees:
        required_levels = {
            get_degree_level(degree)
            for degree in required_degrees
        }

        resume_levels = {
            get_degree_level(degree)
            for degree in resume_degrees
        }

        degree_match = bool(required_levels & resume_levels)

        checks.append({
            "requirement": "Degree",
            "required": sorted(required_degrees),
            "resume_value": sorted(resume_degrees),
            "matched": degree_match,
            "score": 100 if degree_match else 0
        })

    if required_fields and not broad_graduation:
        field_match = bool(required_fields & resume_fields)

        checks.append({
            "requirement": "Field of study",
            "required": sorted(required_fields),
            "resume_value": sorted(resume_fields),
            "matched": field_match,
            "score": 100 if field_match else 0
        })

    minimum_cgpa = jd_requirements.get("minimum_cgpa")

    if minimum_cgpa is None:
        minimum_cgpa = jd_requirements.get("cgpa")

    if minimum_cgpa is not None:
        try:
            minimum_cgpa = float(minimum_cgpa)
            resume_cgpa = resume_education.get("cgpa")

            if resume_cgpa is not None:
                resume_cgpa = float(resume_cgpa)
                cgpa_match = resume_cgpa >= minimum_cgpa
            else:
                cgpa_match = False

            checks.append({
                "requirement": "Minimum CGPA",
                "required": minimum_cgpa,
                "resume_value": resume_cgpa,
                "matched": cgpa_match,
                "score": 100 if cgpa_match else 0
            })

        except (ValueError, TypeError):
            pass

    if not checks:
        return 50, [{
            "requirement": "Education requirements",
            "required": "No specific requirement detected",
            "resume_value": "Not evaluated",
            "matched": None,
            "score": 50
        }]

    score = round(
        sum(check["score"] for check in checks) / len(checks)
    )

    return score, checks


def calculate_project_evidence_score(
    resume_text,
    job_description=None,
    project_requirements=None
):
    resume_normalized = normalize_text(resume_text)
    jd_normalized = normalize_text(job_description or "")

    if project_requirements is not None:
        skill_terms = list(project_requirements)
    else:
        skill_patterns = [
            "python",
            "java",
            "javascript",
            "html",
            "css",
            "sql",
            "database",
            "machine learning",
            "artificial intelligence",
            "natural language processing",
            "nlp",
            "data structures",
            "algorithms",
            "flask",
            "django",
            "react",
            "node.js",
            "git",
            "github",
            "cloud computing",
            "aws",
            "azure",
            "oracle cloud",
            "rest api",
            "api development",
            "object oriented programming",
            "communication",
            "problem solving",
            "analytical skills",
            "microsoft 365",
            "sharepoint"
        ]

        skill_terms = []

        for skill in skill_patterns:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, jd_normalized):
                skill_terms.append(skill)

    unique_terms = []

    for term in skill_terms:
        term = normalize_text(term)

        if term and term not in unique_terms:
            unique_terms.append(term)

    if not unique_terms:
        details = {
            "total_requirements": 0,
            "matched_requirements": 0,
            "missing_requirements": [],
            "matched_terms": []
        }

        evidence = [{
            "requirement": "No recognized technical skills found",
            "evidence": "Not evaluated",
            "matched": None,
            "score": None
        }]

        return 50, evidence, details

    all_evidence = []
    matched_terms = []
    missing_terms = []

    for term in unique_terms:
        pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

        if re.search(pattern, resume_normalized):
            matched_terms.append(term)

            all_evidence.append({
                "requirement": term,
                "evidence": term,
                "matched": True,
                "score": 100
            })
        else:
            missing_terms.append(term)

            all_evidence.append({
                "requirement": term,
                "evidence": "Not found",
                "matched": False,
                "score": 0
            })

    score = round(
        len(matched_terms) / len(unique_terms) * 100
    )

    details = {
        "total_requirements": len(unique_terms),
        "matched_requirements": len(matched_terms),
        "missing_requirements": missing_terms,
        "matched_terms": matched_terms
    }

    evidence = all_evidence[:5]

    return score, evidence, details
