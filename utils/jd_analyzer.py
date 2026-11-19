
import re


EDUCATION_LEVELS = (
    (("high school diploma", "high school"), "High school diploma"),
    (("ged",), "GED"),
    (("associate's degree", "associate degree"), "Associate's degree"),
    (("bachelor's degree", "bachelor degree", "bachelor's", "bachelors", "bachelor"), "Bachelor's degree"),
    (("master's degree", "master degree", "master's", "masters", "master"), "Master's degree"),
    (("ph.d.", "phd"), "Ph.D."),
    (("doctorate", "doctoral degree"), "Doctorate"),
)

DEGREE_PATTERNS = {
    "High school diploma": [r"\bhigh school diploma\b", r"\bhigh school\b"],
    "GED": [r"\bged\b"],
    "Associate's degree": [r"\bassociate(?:'s)? degree\b"],
    "Bachelor's degree": [
        r"\bbachelor(?:'s)?(?: degree)?\b",
        r"\bb\.?\s*tech\b",
        r"\bb\.?\s*e\.?\b",
        r"\bb\.?\s*sc\b",
        r"\bbca\b",
        r"\bb\.?\s*com\b",
        r"\bbachelor of technology\b",
        r"\bbachelor of engineering\b",
        r"\bbachelor of science\b"
    ],
    "Master's degree": [
        r"\bmaster(?:'s)?(?: degree)?\b",
        r"\bm\.?\s*tech\b",
        r"\bm\.?\s*e\.?\b",
        r"\bm\.?\s*sc\b",
        r"\bmca\b",
        r"\bmaster of technology\b",
        r"\bmaster of engineering\b",
        r"\bmaster of science\b"
    ],
    "Ph.D.": [r"\bph\.?\s*d\.?\b", r"\bdoctorate\b", r"\bdoctoral degree\b"]
}

EDUCATION_FIELD_PATTERNS = {
    "Computer Science": [
        r"\bcomputer science and engineering\b",
        r"\bcomputer science\b",
        r"\bcse\b"
    ],
    "Artificial Intelligence": [
        r"\bartificial intelligence\b",
        r"\bai\s*(?:and|&|/)\s*ml\b",
        r"\bai\s*and\s*machine learning\b"
    ],
    "Machine Learning": [r"\bmachine learning\b"],
    "Information Technology": [r"\binformation technology\b"],
    "Electronics": [
        r"\belectronics and communication\b",
        r"\belectrical and electronics\b",
        r"\belectronics\b",
        r"\bece\b",
        r"\beee\b"
    ],
    "Data Science": [r"\bdata science\b"],
    "Mathematics": [r"\bmathematics\b", r"\bmathematical sciences\b"],
    "Statistics": [r"\bstatistics\b"],
    "Business": [r"\bbusiness administration\b", r"\bmanagement studies\b"]
}

PROGRAMMING_LANGUAGES = (
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
    "Go", "Ruby", "PHP", "Swift", "Kotlin", "Rust", "Scala", "R", "SQL"
)

TECHNICAL_REQUIREMENTS = (
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
    "Spring", ".NET", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "Terraform", "Git", "Linux", "PostgreSQL", "MySQL", "MongoDB",
    "Redis", "Kafka", "Spark", "TensorFlow", "PyTorch", "REST APIs",
    "GraphQL", "CI/CD", "machine learning", "data analysis",
    "data structures", "algorithms", "object oriented programming",
    "OOP", "HTML", "CSS", "GitHub", "Oracle Cloud", "Microsoft 365",
    "SharePoint", "Excel", "Power BI", "Tableau", "computer networks",
    "operating systems", "database management", "software development",
    "software testing", "API development", "cloud computing",
    "natural language processing", "deep learning", "computer vision"
)

SPECIALIZED_REQUIREMENTS = (
    "content moderation", "content classification", "content review",
    "policy compliance", "client guidelines", "attention to detail",
    "emotional resilience", "stress management", "comprehension",
    "critical thinking", "decision making", "objectivity", "investigation",
    "issue resolution", "review and classify content", "analyzing content"
)

SOFT_SKILLS = (
    "communication", "teamwork", "collaboration", "interpersonal skills",
    "adaptability", "leadership", "problem solving", "analytical thinking",
    "critical thinking", "decision making", "attention to detail",
    "stress management", "emotional resilience", "comprehension",
    "objectivity", "time management", "self motivation", "conflict resolution"
)


def normalize_text(text):
    text = str(text or "").lower()
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("&", " and ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_term(text, term):
    text = normalize_text(text)
    term = normalize_text(term)

    if not text or not term:
        return False

    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return bool(re.search(pattern, text, re.IGNORECASE))


def extract_education_requirements(text=""):
    text_lower = normalize_text(text)

    education = {
        "degrees": [],
        "fields": [],
        "minimum_cgpa": None,
        "broad_graduation": False
    }

    broad_patterns = (
        r"\bany degree\b",
        r"\bany graduate\b",
        r"\bany graduates\b",
        r"\bany bachelor's degree\b",
        r"\bany bachelor degree\b",
        r"\bdegree in any discipline\b",
        r"\bgraduation in any discipline\b",
        r"\bgraduation in any stream\b",
        r"\bdegree in any stream\b",
        r"\bany stream\b",
        r"\bany discipline\b",
        r"\bany educational background\b",
        r"\ball degree holders\b",
        r"\bgraduates from any stream\b",
        r"\bgraduates in any discipline\b",
        r"\bcandidates with any degree\b",
        r"\bany degree holder\b",
        r"\bdegree in any field\b",
        r"\bundergraduate degree in any field\b",
        r"\bany bachelor's or master's degree\b",
        r"\bany degree qualification\b",
        r"\bgraduate in any field\b",
        r"\bopen to all graduates\b"
    )

    education["broad_graduation"] = any(
        re.search(pattern, text_lower, re.IGNORECASE)
        for pattern in broad_patterns
    )

    for degree, patterns in DEGREE_PATTERNS.items():
        if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
            education["degrees"].append(degree)

    for field, patterns in EDUCATION_FIELD_PATTERNS.items():
        if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns):
            education["fields"].append(field)

    cgpa_patterns = (
        r"\bminimum\s+(?:cgpa|gpa)\s*(?:of|:)?\s*(\d+(?:\.\d+)?)",
        r"\b(?:cgpa|gpa)\s*(?:of|:|>=|at least)\s*(\d+(?:\.\d+)?)",
        r"\b(?:cgpa|gpa)\s*(?:should be|must be)\s*(?:at least\s*)?(\d+(?:\.\d+)?)"
    )

    for pattern in cgpa_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 0 < value <= 10:
                education["minimum_cgpa"] = value
                break

    return education


def classify_requirement_type(requirement, text=None, mandatory_words=()):
    requirement_lower = normalize_text(requirement)
    text_lower = normalize_text(text)

    preferred_words = (
        "preferred", "preferably", "nice to have", "desired",
        "bonus", "an advantage", "not mandatory",
        "would be a plus", "good to have"
    )

    if any(phrase in requirement_lower for phrase in preferred_words):
        return "Preferred"

    if any(phrase in text_lower for phrase in preferred_words):
        return "Preferred"

    if any(normalize_text(word) in requirement_lower for word in mandatory_words or ()):
        return "Required"

    return "Required"


def extract_jd_skill_requirements(text):
    text_lower = normalize_text(text)

    requirements = {
        "required_programming_languages": [],
        "required_technical_requirements": [],
        "preferred_programming_languages": [],
        "preferred_technical_requirements": [],
        "required_specialized_requirements": [],
        "preferred_specialized_requirements": [],
        "required_soft_skills": [],
        "preferred_soft_skills": []
    }

    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?;\n]+", str(text or "").lower())
        if sentence.strip()
    ]

    def find_context(term):
        matches = [
            sentence for sentence in sentences
            if contains_term(sentence, term)
        ]
        return " ".join(matches) if matches else text_lower

    def add_requirement(term, category, preferred=False):
        prefix = "preferred_" if preferred else "required_"
        key = prefix + category

        if term not in requirements[key]:
            requirements[key].append(term)

    groups = (
        ("programming_languages", PROGRAMMING_LANGUAGES),
        ("technical_requirements", TECHNICAL_REQUIREMENTS),
        ("specialized_requirements", SPECIALIZED_REQUIREMENTS),
        ("soft_skills", SOFT_SKILLS)
    )

    for category, terms in groups:
        for term in terms:
            if not contains_term(text_lower, term):
                continue

            context = find_context(term)
            preferred = classify_requirement_type(term, context) == "Preferred"
            add_requirement(term, category, preferred)

    for key in requirements:
        requirements[key] = sorted(set(requirements[key]))

    return requirements


def extract_requirement_sections(text):
    text = str(text or "")
    text_lower = text.lower()

    headings = (
        ("required qualifications", "required"),
        ("minimum qualifications", "required"),
        ("required skills", "required"),
        ("must have", "required"),
        ("requirements", "required"),
        ("what are we looking for", "required"),
        ("roles and responsibilities", "required"),
        ("qualifications", "required"),
        ("preferred qualifications", "preferred"),
        ("desired qualifications", "preferred"),
        ("preferred skills", "preferred"),
        ("nice to have", "preferred"),
        ("good to have", "preferred")
    )

    markers = []

    for heading, section_type in headings:
        start = 0

        while True:
            position = text_lower.find(heading, start)
            if position == -1:
                break

            before = text_lower[position - 1] if position else " "
            after_position = position + len(heading)
            after = text_lower[after_position] if after_position < len(text_lower) else " "

            valid_before = before.isspace() or before in ".;!?:\n"
            valid_after = after.isspace() or after in ":.-\n"

            if valid_before and valid_after:
                markers.append((position, after_position, section_type))

            start = after_position

    markers.sort(key=lambda item: item[0])

    sections = {"required": [], "preferred": []}

    for index, (_, content_start, section_type) in enumerate(markers):
        end = markers[index + 1][0] if index + 1 < len(markers) else len(text)
        content = text[content_start:end].strip(" \t\r\n:.-")

        if content:
            sections[section_type].append(content)

    return {
        "required": " ".join(sections["required"]),
        "preferred": " ".join(sections["preferred"])
    }


def extract_work_locations(text):
    text = str(text or "")
    text_lower = text.lower()

    location_indicators = (
        ("work from home", "Remote"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("on-site", "On-site"),
        ("onsite", "On-site"),
        ("office-based", "Office"),
        ("rotational shifts", "Rotational shifts"),
        ("travel required", "Travel required")
    )

    work_locations = []

    for phrase, label in location_indicators:
        if contains_term(text_lower, phrase) and label not in work_locations:
            work_locations.append(label)

    for marker in ("location:", "locations:", "based in", "located in"):
        position = text_lower.find(marker)
        if position == -1:
            continue

        candidate = text[position + len(marker):]
        candidate = re.split(r"[.;\n]", candidate, maxsplit=1)[0]
        candidate = candidate.strip(" -:\t")

        if candidate:
            label = candidate.title()
            if label not in work_locations:
                work_locations.append(label)

    return work_locations


def analyze_job_description(text):
    text = str(text or "").strip()

    education = extract_education_requirements(text)
    skills = extract_jd_skill_requirements(text)
    sections = extract_requirement_sections(text)
    work_locations = extract_work_locations(text)

    requirements = []

    categories = (
        ("required_programming_languages", "Programming", "Required"),
        ("required_technical_requirements", "Technical", "Required"),
        ("preferred_programming_languages", "Programming", "Preferred"),
        ("preferred_technical_requirements", "Technical", "Preferred"),
        ("required_specialized_requirements", "Specialized", "Required"),
        ("preferred_specialized_requirements", "Specialized", "Preferred"),
        ("required_soft_skills", "Soft Skills", "Required"),
        ("preferred_soft_skills", "Soft Skills", "Preferred")
    )

    for key, category, requirement_type in categories:
        for name in skills[key]:
            requirements.append({
                "name": name,
                "category": category,
                "type": requirement_type
            })

    return {
        "education": education,
        "skills": skills,
        "required_section": sections["required"],
        "preferred_section": sections["preferred"],
        "requirements": requirements,
        "work_locations": work_locations,
        "requirement_count": len(requirements)
    }
