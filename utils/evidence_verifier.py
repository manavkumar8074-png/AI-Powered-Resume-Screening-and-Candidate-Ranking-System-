import re


def normalize_text(text):
    text = str(text or "").lower()

    text = text.replace(
        "object-oriented",
        "object oriented"
    )

    text = text.replace(
        "problem-solving",
        "problem solving"
    )

    text = text.replace(
        "node js",
        "node.js"
    )

    text = text.replace(
        "nodejs",
        "node.js"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


SECTION_LABELS = {
    "skills": [
        "skills",
        "technical skills",
        "technical skills and tools",
        "core skills",
        "key skills",
        "professional skills"
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "project experience"
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internships"
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses"
    ],
    "education": [
        "education",
        "academic background",
        "educational qualifications",
        "qualifications"
    ]
}


def clean_text(text):
    text = str(text or "")
    text = text.replace(
        "\r",
        "\n"
    )
    return text


def is_section_heading(line):
    line = str(line or "").strip()

    if not line:
        return None

    normalized = normalize_text(line)

    normalized = re.sub(
        r"[:\-]+$",
        "",
        normalized
    ).strip()

    for section_name, labels in SECTION_LABELS.items():
        for label in labels:
            if normalized == normalize_text(label):
                return section_name

    return None


def extract_resume_sections(resume_text):
    text = clean_text(resume_text)

    sections = {
        "skills": "",
        "projects": "",
        "experience": "",
        "certifications": "",
        "education": "",
        "other": ""
    }

    current_section = "other"

    for line in text.split("\n"):
        heading = is_section_heading(line)

        if heading:
            current_section = heading
            continue

        if current_section not in sections:
            current_section = "other"

        sections[current_section] += line + "\n"

    return {
        key: value.strip()
        for key, value in sections.items()
    }


def normalize_skill(skill):
    skill = str(skill or "").strip().lower()

    replacements = {
        "nodejs": "node.js",
        "node js": "node.js",
        "c sharp": "c#",
        "object-oriented programming":
            "object oriented programming",
        "object-oriented":
            "object oriented programming",
        "problem-solving":
            "problem solving",
        "software development lifecycle":
            "sdlc",
        "software development life cycle":
            "sdlc",
        "ml":
            "machine learning",
        "natural language processing":
            "nlp"
    }

    return replacements.get(
        skill,
        skill
    )


SKILL_ALIASES = {
    "python": [
        r"\bpython\b"
    ],
    "java": [
        r"\bjava\b"
    ],
    "c++": [
        r"\bc\+\+\b"
    ],
    "c": [
        r"(?<![a-z])c(?![a-z+#])"
    ],
    "c#": [
        r"\bc#\b",
        r"\bc\s*sharp\b"
    ],
    "javascript": [
        r"\bjavascript\b"
    ],
    "node.js": [
        r"\bnode\.js\b",
        r"\bnodejs\b",
        r"\bnode\s+js\b"
    ],
    "sql": [
        r"\bsql\b"
    ],
    "sdlc": [
        r"\bsdlc\b",
        r"\bsoftware\s+development\s+life\s+cycle\b",
        r"\bsoftware\s+development\s+lifecycle\b"
    ],
    "object oriented programming": [
        r"\boop\b",
        r"\bobject\s+oriented\s+programming\b",
        r"\bobject[-\s]+oriented\b"
    ],
    "problem solving": [
        r"\bproblem\s+solving\b",
        r"\bproblem-solving\b"
    ],
    "analytical skills": [
        r"\banalytical\s+skills?\b",
        r"\banalytical\s+thinking\b"
    ],
    "communication": [
        r"\bcommunication\s+skills?\b",
        r"\bfluent\s+communication\b",
        r"\bverbal\s+communication\b"
    ],
    "interpersonal skills": [
        r"\binterpersonal\s+skills?\b"
    ],
    "machine learning": [
        r"\bmachine\s+learning\b",
        r"\bml\b"
    ],
    "nlp": [
        r"\bnlp\b",
        r"\bnatural\s+language\s+processing\b"
    ],
    "git": [
        r"\bgit\b"
    ],
    "github": [
        r"\bgithub\b"
    ],
    "oracle cloud": [
        r"\boracle\s+cloud\b"
    ],
    "html": [
        r"\bhtml\b"
    ],
    "css": [
        r"\bcss\b"
    ],
    "database": [
        r"\bdatabase\b",
        r"\bdatabases\b"
    ],
    "data structures": [
        r"\bdata\s+structures?\b"
    ],
    "algorithms": [
        r"\balgorithms?\b"
    ],
    "microsoft 365": [
        r"\bmicrosoft\s+365\b",
        r"\bm365\b"
    ],
    "sharepoint": [
        r"\bsharepoint\b"
    ],
    "power apps": [
        r"\bpower\s+apps\b",
        r"\bpowerapps\b"
    ],
    "power automate": [
        r"\bpower\s+automate\b"
    ],
    "power platform": [
        r"\bpower\s+platform\b"
    ]
}


def skill_matches_text(skill, text):
    skill = normalize_skill(skill)
    text = str(text or "")

    patterns = SKILL_ALIASES.get(skill)

    if patterns is None:
        normalized_skill = normalize_text(skill)

        if not normalized_skill:
            return False

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(normalized_skill)
            + r"(?![a-z0-9])"
        )

        try:
            return bool(
                re.search(
                    pattern,
                    normalize_text(text),
                    re.IGNORECASE
                )
            )
        except re.error:
            return False

    for pattern in patterns:
        try:
            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True
        except re.error:
            continue

    return False


def get_evidence_sources(skill, sections):
    sources = []

    section_order = [
        ("skills", "Skills"),
        ("projects", "Projects"),
        ("experience", "Experience"),
        ("certifications", "Certifications"),
        ("education", "Education")
    ]

    for section_key, section_name in section_order:
        section_text = sections.get(
            section_key,
            ""
        )

        if skill_matches_text(
            skill,
            section_text
        ):
            sources.append(section_name)

    if not sources:
        full_text = " ".join(
            sections.values()
        )

        if skill_matches_text(
            skill,
            full_text
        ):
            sources.append("Resume Text")

    return sources


def calculate_evidence_strength(sources):
    source_set = set(sources)

    if (
        "Projects" in source_set
        and "Experience" in source_set
    ):
        return "Very Strong", 100

    if (
        "Skills" in source_set
        and (
            "Projects" in source_set
            or "Experience" in source_set
        )
    ):
        return "Strong", 90

    if "Projects" in source_set:
        return "Strong", 85

    if "Experience" in source_set:
        return "Strong", 85

    if "Skills" in source_set:
        return "Moderate", 65

    if "Certifications" in source_set:
        return "Weak", 45

    if "Education" in source_set:
        return "Weak", 40

    if "Resume Text" in source_set:
        return "Mentioned", 30

    return "Missing", 0


def verify_skill_evidence(
    resume_text,
    required_skills,
    preferred_skills
):
    sections = extract_resume_sections(
        resume_text
    )

    required_skills = {
        normalize_skill(skill)
        for skill in required_skills
        if str(skill).strip()
    }

    preferred_skills = {
        normalize_skill(skill)
        for skill in preferred_skills
        if str(skill).strip()
    }

    results = []

    for skill in sorted(
        required_skills,
        key=str
    ):
        sources = get_evidence_sources(
            skill,
            sections
        )

        strength, score = calculate_evidence_strength(
            sources
        )

        matched = bool(sources)

        results.append({
            "skill": skill,
            "requirement_type": "Required",
            "matched": matched,
            "strength": strength,
            "score": score,
            "sources": sources
        })

    for skill in sorted(
        preferred_skills,
        key=str
    ):
        sources = get_evidence_sources(
            skill,
            sections
        )

        strength, score = calculate_evidence_strength(
            sources
        )

        matched = bool(sources)

        results.append({
            "skill": skill,
            "requirement_type": "Preferred",
            "matched": matched,
            "strength": strength,
            "score": score,
            "sources": sources
        })

    required_results = [
        item
        for item in results
        if item["requirement_type"] == "Required"
    ]

    preferred_results = [
        item
        for item in results
        if item["requirement_type"] == "Preferred"
    ]

    def average_score(items):
        if not items:
            return 0.0

        return round(
            sum(
                float(item["score"])
                for item in items
            ) / len(items),
            2
        )

    required_evidence_score = average_score(
        required_results
    )

    preferred_evidence_score = average_score(
        preferred_results
    )

    evidence_score = average_score(
        results
    )

    matched = [
        item["skill"]
        for item in results
        if item["matched"]
    ]

    missing = [
        item["skill"]
        for item in results
        if not item["matched"]
    ]

    required_matched = [
        item["skill"]
        for item in required_results
        if item["matched"]
    ]

    preferred_matched = [
        item["skill"]
        for item in preferred_results
        if item["matched"]
    ]

    required_missing = [
        item["skill"]
        for item in required_results
        if not item["matched"]
    ]

    preferred_missing = [
        item["skill"]
        for item in preferred_results
        if not item["matched"]
    ]

    return {
        "results": results,
        "evidence_score": evidence_score,
        "required_evidence_score":
            required_evidence_score,
        "preferred_evidence_score":
            preferred_evidence_score,
        "matched": matched,
        "missing": missing,
        "required_matched": required_matched,
        "preferred_matched": preferred_matched,
        "required_missing": required_missing,
        "preferred_missing": preferred_missing,
        "sections": sections
    }


def get_evidence_summary(evidence_results):
    if not evidence_results:
        return "No evidence records available."

    total = len(evidence_results)

    supported = sum(
        1
        for item in evidence_results
        if item.get("matched", False)
    )

    not_demonstrated = total - supported

    average_score = sum(
        float(item.get("score", 0))
        for item in evidence_results
    ) / total

    required_items = [
        item
        for item in evidence_results
        if str(
            item.get(
                "requirement_type",
                ""
            )
        ).lower() == "required"
    ]

    preferred_items = [
        item
        for item in evidence_results
        if str(
            item.get(
                "requirement_type",
                ""
            )
        ).lower() == "preferred"
    ]

    required_supported = sum(
        1
        for item in required_items
        if item.get("matched", False)
    )

    preferred_supported = sum(
        1
        for item in preferred_items
        if item.get("matched", False)
    )

    if required_items:
        required_summary = (
            f"{required_supported}/"
            f"{len(required_items)} required skills supported"
        )
    else:
        required_summary = (
            "No required skill evidence records"
        )

    if preferred_items:
        preferred_summary = (
            f"{preferred_supported}/"
            f"{len(preferred_items)} preferred skills supported"
        )
    else:
        preferred_summary = (
            "No preferred skill evidence records"
        )

    return (
        f"{supported}/{total} skills supported. "
        f"{not_demonstrated} skills not demonstrated. "
        f"Average evidence score: "
        f"{round(average_score, 2)}%. "
        f"{required_summary}. "
        f"{preferred_summary}."
    )