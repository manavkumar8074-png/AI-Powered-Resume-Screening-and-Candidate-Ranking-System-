from flask import Flask, request, render_template

from markupsafe import escape

from utils.resume_extractor import (
    extract_text_from_resume,
    SUPPORTED_EXTENSIONS
)

from utils.text_preprocessor import preprocess_text

from utils.resumematcher import calculate_similarity

from utils.skill_extractor import (
    extract_skills,
    extract_skill_sections,
    detect_proficiency
)

from utils.jd_analyzer import (
    extract_education_requirements,
    analyze_job_description
)

from utils.resume_analyzer import (
    extract_resume_education,
    calculate_education_score,
    calculate_project_evidence_score
)

from utils.evidence_verifier import (
    verify_skill_evidence,
    get_evidence_summary
)

from utils.gpt_resume_analyzer import analyze_resume_with_gpt

import os
import uuid
import re


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["LAST_RESULTS"] = {}


CORE_TECHNICAL_SKILLS = {

    "python",
    "java",
    "javascript",
    "html",
    "css",
    "sql",
    "database",
    "object oriented programming",
    "machine learning",
    "nlp",
    "data structures",
    "algorithms",
    "git",
    "github",
    "oracle cloud",
    "c++",
    "c",
    "c#",
    "node.js",
    "sdlc"

}


SOFT_SKILLS = {

    "analytical skills",
    "communication",
    "problem solving",
    "interpersonal skills"

}


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
    ]

}


def make_list(items):

    if not items:

        return "<li>None identified.</li>"

    return "".join(

        f"<li>{escape(str(item).title())}</li>"

        for item in sorted(
            items,
            key=str
        )

    )


def make_strength_list(items):

    if not items:

        return "<li>No specific strengths detected.</li>"

    return "".join(

        f"<li>✓ {escape(str(item).title())}</li>"

        for item in sorted(
            items,
            key=str
        )

    )


def make_gap_list(items):

    if not items:

        return "<li>No significant gaps identified.</li>"

    return "".join(

        f"<li>• {escape(str(item).title())}</li>"

        for item in sorted(
            items,
            key=str
        )

    )


def normalize_skill_name(skill):

    skill = str(skill).strip().lower()

    replacements = {

        "nodejs":
            "node.js",

        "node js":
            "node.js",

        "c sharp":
            "c#",

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


def augment_skills_from_text(
    text,
    skills
):

    result = {

        normalize_skill_name(skill)

        for skill in skills

    }

    text = str(
        text or ""
    )

    for skill, patterns in SKILL_ALIASES.items():

        for pattern in patterns:

            try:

                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                ):

                    result.add(skill)

                    break

            except re.error:

                continue

    return result


def calculate_evidence_category_score(
    evidence_results,
    skill_set,
    requirement_type
):

    scores = []

    normalized_skills = {

        normalize_skill_name(skill)

        for skill in skill_set

    }

    for item in evidence_results:

        skill = normalize_skill_name(

            item.get(
                "skill",
                ""
            )

        )

        item_type = str(

            item.get(
                "requirement_type",
                ""
            )

        )

        if skill not in normalized_skills:

            continue

        if (

            item_type.lower()

            != requirement_type.lower()

        ):

            continue

        try:

            scores.append(

                float(

                    item.get(
                        "score",
                        0
                    )

                )

            )

        except Exception:

            pass

    if not scores:

        return None

    return round(

        sum(scores) / len(scores),

        2

    )


def blend_keyword_and_evidence(
    keyword_score,
    evidence_score,
    evidence_weight
):

    if evidence_score is None:

        return round(
            keyword_score,
            2
        )

    result = (

        keyword_score
        * (1 - evidence_weight)

    ) + (

        evidence_score
        * evidence_weight

    )

    return round(
        result,
        2
    )


def calculate_improved_project_relevance(
    resume_text,
    job_description,
    required_skills,
    preferred_skills
):

    text = str(
        resume_text or ""
    ).lower()

    required = {

        normalize_skill_name(skill)

        for skill in required_skills

    }

    preferred = {

        normalize_skill_name(skill)

        for skill in preferred_skills

    }

    all_relevant = (
        required
        |
        preferred
    )

    if not all_relevant:

        return {

            "score": 0.0,

            "label": "Low Relevance",

            "evidence": [],

            "details": {}

        }

    project_positions = []

    for match in re.finditer(
        r"\bprojects?\b",
        text,
        re.IGNORECASE
    ):

        project_positions.append(
            match.start()
        )

    if not project_positions:

        project_positions = [0]

    project_windows = []

    for position in project_positions:

        start = max(
            0,
            position - 100
        )

        end = min(
            len(text),
            position + 1600
        )

        project_windows.append(

            text[start:end]

        )

    project_text = " ".join(
        project_windows
    )

    required_matches = []

    preferred_matches = []

    for skill in required:

        patterns = SKILL_ALIASES.get(

            skill,

            [
                r"\b"
                + re.escape(skill)
                + r"\b"
            ]

        )

        found = False

        for pattern in patterns:

            try:

                if re.search(
                    pattern,
                    project_text,
                    re.IGNORECASE
                ):

                    found = True

                    break

            except re.error:

                continue

        if found:

            required_matches.append(
                skill
            )

    for skill in preferred:

        patterns = SKILL_ALIASES.get(

            skill,

            [
                r"\b"
                + re.escape(skill)
                + r"\b"
            ]

        )

        found = False

        for pattern in patterns:

            try:

                if re.search(
                    pattern,
                    project_text,
                    re.IGNORECASE
                ):

                    found = True

                    break

            except re.error:

                continue

        if found:

            preferred_matches.append(
                skill
            )

    required_coverage = (

        len(required_matches)
        /
        len(required)

        if required

        else 1

    )

    preferred_coverage = (

        len(preferred_matches)
        /
        len(preferred)

        if preferred

        else 1

    )

    implementation_terms = [

        "developed",
        "implemented",
        "designed",
        "built",
        "created",
        "integrated",
        "tested",
        "deployed",
        "trained",
        "automated",
        "programmed",
        "configured",
        "developing",
        "implementation"

    ]

    implementation_count = 0

    for term in implementation_terms:

        if term in project_text:

            implementation_count += 1

    implementation_score = min(

        implementation_count / 5,
        1

    )

    project_depth = min(

        len(project_text) / 2500,
        1

    )

    score = (

        required_coverage * 55

        +

        preferred_coverage * 10

        +

        implementation_score * 25

        +

        project_depth * 10

    )

    score = round(

        min(score, 100),

        2

    )

    if score >= 85:

        label = "Highly Relevant"

    elif score >= 70:

        label = "Strongly Relevant"

    elif score >= 50:

        label = "Moderately Relevant"

    elif score >= 30:

        label = "Low Relevance"

    else:

        label = "Very Low Relevance"

    evidence = []

    for skill in required_matches:

        evidence.append(

            "Required skill demonstrated in "
            f"project evidence: {skill}"

        )

    for skill in preferred_matches:

        evidence.append(

            "Preferred skill demonstrated in "
            f"project evidence: {skill}"

        )

    if implementation_count:

        evidence.append(

            f"{implementation_count} implementation-oriented "
            "project terms detected"

        )

    return {

        "score": score,

        "label": label,

        "evidence": evidence,

        "details": {

            "required_matches":
                required_matches,

            "preferred_matches":
                preferred_matches,

            "implementation_count":
                implementation_count,

            "project_depth":
                round(
                    project_depth * 100,
                    2
                )

        }

    }


def generate_ai_candidate_review(candidate):

    score = float(

        candidate.get(
            "overall_score",
            0
        )

    )

    recommendation = str(

        candidate.get(
            "recommendation",
            ""
        )

    )

    matched_technical = sorted(

        candidate.get(
            "matched_technical",
            []
        ),

        key=str

    )

    matched_specialized = sorted(

        candidate.get(
            "matched_specialized_required",
            []
        ),

        key=str

    )

    matched_preferred = sorted(

        candidate.get(
            "matched_preferred",
            []
        ),

        key=str

    )

    matched_soft = sorted(

        candidate.get(
            "matched_soft",
            []
        ),

        key=str

    )

    missing_technical = sorted(

        candidate.get(
            "missing_technical",
            []
        ),

        key=str

    )

    missing_specialized = sorted(

        candidate.get(
            "missing_specialized_required",
            []
        ),

        key=str

    )

    missing_preferred = sorted(

        candidate.get(
            "missing_preferred",
            []
        ),

        key=str

    )

    resume_education = candidate.get(

        "resume_education",
        {}

    )

    project_relevance = str(

        candidate.get(
            "project_relevance",
            "Low"
        )

    )

    project_score = float(

        candidate.get(
            "project_score",
            0
        )

    )

    evidence_score = float(

        candidate.get(
            "evidence_score",
            0
        )

    )

    similarity_score = float(

        candidate.get(
            "similarity_score",
            0
        )

    )

    education_score = float(

        candidate.get(
            "education_score",
            0
        )

    )

    def skill_text(
        items,
        limit=5
    ):

        values = [

            str(item)
            .replace("_", " ")
            .title()

            for item in items[:limit]

        ]

        if not values:

            return ""

        if len(values) == 1:

            return values[0]

        if len(values) == 2:

            return (
                f"{values[0]} and "
                f"{values[1]}"
            )

        return (

            ", ".join(values[:-1])

            + f", and {values[-1]}"

        )

    strengths = []

    gaps = []

    if matched_technical:

        strengths.append(

            "required technical skills such as "
            + skill_text(
                matched_technical
            )

        )

    if matched_specialized:

        strengths.append(

            "specialized requirements including "
            + skill_text(
                matched_specialized
            )

        )

    if matched_preferred:

        strengths.append(

            "additional preferred skills such as "
            + skill_text(
                matched_preferred
            )

        )

    if matched_soft:

        strengths.append(

            "soft skills including "
            + skill_text(
                matched_soft
            )

        )

    if project_score >= 70:

        strengths.append(

            f"relevant project work with a "
            f"project relevance score of "
            f"{project_score:.1f}%"

        )

    elif project_score >= 40:

        strengths.append(

            f"moderately relevant project work "
            f"with a project relevance score of "
            f"{project_score:.1f}%"

        )

    if evidence_score >= 70:

        strengths.append(

            f"strong resume evidence supporting "
            f"the identified skills "
            f"({evidence_score:.1f}%)"

        )

    if missing_technical:

        gaps.append(

            "missing or insufficiently demonstrated "
            "technical requirements such as "
            + skill_text(
                missing_technical
            )

        )

    if missing_specialized:

        gaps.append(

            "specialized requirements not clearly "
            "demonstrated, including "
            + skill_text(
                missing_specialized
            )

        )

    if missing_preferred:

        gaps.append(

            "preferred skills not clearly "
            "demonstrated, including "
            + skill_text(
                missing_preferred
            )

        )

    if project_score < 40:

        gaps.append(

            "limited project evidence directly "
            "connected to the job requirements"

        )

    if evidence_score < 50:

        gaps.append(

            "limited supporting evidence for "
            "the skills listed in the resume"

        )

    education_parts = []

    if isinstance(
        resume_education,
        dict
    ):

        degree = resume_education.get(
            "degree"
        )

        branch = resume_education.get(
            "branch"
        )

        cgpa = resume_education.get(
            "cgpa"
        )

        if degree:

            education_parts.append(

                f"degree information ({degree})"

            )

        if branch:

            education_parts.append(

                f"branch information ({branch})"

            )

        if cgpa:

            education_parts.append(

                f"CGPA of {cgpa}"

            )

    if education_parts:

        education_sentence = (

            "The education information extracted "
            "from the resume includes "

            + ", ".join(
                education_parts
            )

            + "."

        )

    else:

        education_sentence = (

            "The resume does not provide enough "
            "structured education information "
            "for a detailed education summary."

        )

    if score >= 65:

        final_decision = (
            "Suitable for the Job"
        )

    else:

        final_decision = (
            "Not Suitable for the Job"
        )

    if final_decision == "Suitable for the Job":

        if strengths:

            selection_reason = (

                "The candidate is selected by the "
                "AI screening system because the "
                "resume demonstrates "

                + "; ".join(
                    strengths[:4]
                )

                + "."

            )

        else:

            selection_reason = (

                "The candidate meets the screening "
                "threshold based on the combined "
                "technical, specialized, education, "
                "project and evidence-based analysis."

            )

        if gaps:

            not_selection_reason = (

                "Although the candidate meets the "
                "screening threshold, the following "
                "areas should be considered as gaps: "

                + "; ".join(
                    gaps[:3]
                )

                + "."

            )

        else:

            not_selection_reason = (

                "No major job-related gaps were "
                "identified from the available "
                "resume information."

            )

    else:

        if gaps:

            not_selection_reason = (

                "The candidate is not selected by "
                "the AI screening system because "

                + "; ".join(
                    gaps[:4]
                )

                + "."

            )

        else:

            not_selection_reason = (

                "The candidate does not reach the "
                "required screening threshold based "
                "on the combined job-related analysis."

            )

        if strengths:

            selection_reason = (

                "The resume does contain positive "
                "job-related evidence, including "

                + "; ".join(
                    strengths[:3]
                )

                + ", but these strengths are not "
                "sufficient to reach the current "
                "screening threshold."

            )

        else:

            selection_reason = (

                "The analysis did not identify enough "
                "job-related strengths to meet the "
                "current screening threshold."

            )

    if score >= 80:

        opening = (

            "The resume demonstrates strong "
            "overall alignment with the analyzed "
            "job requirements."

        )

    elif score >= 65:

        opening = (

            "The resume demonstrates good overall "
            "alignment with the analyzed job "
            "requirements."

        )

    elif score >= 50:

        opening = (

            "The resume demonstrates moderate "
            "alignment with the analyzed job "
            "requirements, with several areas "
            "requiring attention."

        )

    else:

        opening = (

            "The resume demonstrates limited "
            "alignment with the analyzed job "
            "requirements."

        )

    if strengths:

        strength_sentence = (

            "The main strengths identified are "

            + "; ".join(
                strengths[:4]
            )

            + "."

        )

    else:

        strength_sentence = (

            "The analysis did not identify enough "
            "strong requirement matches to "
            "highlight specific strengths."

        )

    if gaps:

        gap_sentence = (

            "The main gaps identified are "

            + "; ".join(
                gaps[:4]
            )

            + "."

        )

    else:

        gap_sentence = (

            "No major requirement gaps were "
            "identified from the available "
            "resume evidence."

        )

    if similarity_score >= 70:

        similarity_sentence = (

            f"The resume-to-job-description "
            f"similarity is "
            f"{similarity_score:.1f}%, indicating "
            "substantial textual alignment."

        )

    elif similarity_score >= 45:

        similarity_sentence = (

            f"The resume-to-job-description "
            f"similarity is "
            f"{similarity_score:.1f}%, showing "
            "partial textual alignment."

        )

    else:

        similarity_sentence = (

            f"The resume-to-job-description "
            f"similarity is "
            f"{similarity_score:.1f}%, indicating "
            "limited textual alignment."

        )

    review = " ".join(

        [

            opening,

            strength_sentence,

            education_sentence,

            (

                f"Project relevance is assessed as "
                f"{project_relevance.lower()} at "
                f"{project_score:.1f}%."

            ),

            (

                f"Education score is "
                f"{education_score:.1f}%."

            ),

            (

                f"Evidence-based skill score is "
                f"{evidence_score:.1f}%."

            ),

            similarity_sentence,

            gap_sentence,

            (

                f"The overall AI screening score is "
                f"{score:.1f}% with a "
                f"{recommendation} classification."

            )

        ]

    )

    matched_skills = (

        matched_technical

        +

        matched_specialized

        +

        matched_preferred

        +

        matched_soft

    )

    missing_skills = (

        missing_technical

        +

        missing_specialized

        +

        missing_preferred

    )

    return {

        "review":
            review,

        "final_decision":
            final_decision,

        "selection_reason":
            selection_reason,

        "not_selection_reason":
            not_selection_reason,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills

    }


def analyze_candidate(
    file_path,
    filename,
    job_description
):

    try:

        extracted_text = extract_text_from_resume(
            file_path
        )

    except Exception as e:

        return {

            "filename":
                filename,

            "error":
                "Could not extract text from this resume: "
                + str(e)

        }

    if not extracted_text or not extracted_text.strip():

        return {

            "filename":
                filename,

            "error":
                "Could not extract text from this resume."

        }

    try:

        cleaned_resume = preprocess_text(
            extracted_text
        )

        cleaned_jd = preprocess_text(
            job_description
        )

    except Exception as e:

        return {

            "filename":
                filename,

            "error":
                "Text preprocessing failed: "
                + str(e)

        }

    try:

        similarity_score = calculate_similarity(
            cleaned_resume,
            cleaned_jd
        )

    except Exception:

        similarity_score = 0.0

    try:

        resume_skills = set(

            extract_skills(
                extracted_text
            )

        )

    except Exception:

        resume_skills = set()

    resume_skills = augment_skills_from_text(

        extracted_text,
        resume_skills

    )

    try:

        jd_skills = set(

            extract_skills(
                job_description
            )

        )

    except Exception:

        jd_skills = set()

    jd_skills = augment_skills_from_text(

        job_description,
        jd_skills

    )

    try:

        required_skills, preferred_skills = (

            extract_skill_sections(
                job_description
            )

        )

    except Exception:

        required_skills = set()

        preferred_skills = set()

    required_skills = {

        normalize_skill_name(skill)

        for skill in required_skills

    }

    preferred_skills = {

        normalize_skill_name(skill)

        for skill in preferred_skills

    }

    try:

        jd_analysis = analyze_job_description(
            job_description
        )

    except Exception:

        jd_analysis = {

            "education": {},
            "skills": {},
            "requirements": [],
            "work_locations": []

        }

    jd_skill_data = jd_analysis.get(
        "skills",
        {}
    )

    required_programming = {

        normalize_skill_name(skill)

        for skill in jd_skill_data.get(
            "required_programming_languages",
            []
        )

    }

    preferred_programming = {

        normalize_skill_name(skill)

        for skill in jd_skill_data.get(
            "preferred_programming_languages",
            []
        )

    }

    required_technical = {

        normalize_skill_name(skill)

        for skill in jd_skill_data.get(
            "required_technical_requirements",
            []
        )

    }

    preferred_technical = {

        normalize_skill_name(skill)

        for skill in jd_skill_data.get(
            "preferred_technical_requirements",
            []
        )

    }

    required_skills.update(
        required_programming
    )

    required_skills.update(
        required_technical
    )

    preferred_skills.update(
        preferred_programming
    )

    preferred_skills.update(
        preferred_technical
    )

    required_skills = {

        skill

        for skill in required_skills

        if skill

    }

    preferred_skills = {

        skill

        for skill in preferred_skills

        if skill

    }

    specialized_required = (

        required_skills

        -

        CORE_TECHNICAL_SKILLS

        -

        SOFT_SKILLS

    )

    specialized_preferred = (

        preferred_skills

        -

        CORE_TECHNICAL_SKILLS

        -

        SOFT_SKILLS

    )

    technical_required = (

        required_skills

        .intersection(
            CORE_TECHNICAL_SKILLS
        )

    )

    matched_technical = (

        resume_skills

        .intersection(
            technical_required
        )

    )

    missing_technical = (

        technical_required

        -

        resume_skills

    )

    matched_specialized_required = (

        resume_skills

        .intersection(
            specialized_required
        )

    )

    missing_specialized_required = (

        specialized_required

        -

        resume_skills

    )

    matched_specialized_preferred = (

        resume_skills

        .intersection(
            specialized_preferred
        )

    )

    missing_specialized_preferred = (

        specialized_preferred

        -

        resume_skills

    )

    matched_preferred = (

        resume_skills

        .intersection(
            specialized_preferred
        )

    )

    missing_preferred = (

        specialized_preferred

        -

        resume_skills

    )

    soft_required = (

        required_skills

        .intersection(
            SOFT_SKILLS
        )

    )

    matched_soft = (

        resume_skills

        .intersection(
            soft_required
        )

    )

    missing_soft = (

        soft_required

        -

        resume_skills

    )

    if technical_required:

        technical_keyword_score = round(

            (

                len(matched_technical)

                /

                len(technical_required)

            ) * 100,

            2

        )

    else:

        technical_keyword_score = 100.0

    if specialized_required:

        specialized_keyword_score = round(

            (

                len(matched_specialized_required)

                /

                len(specialized_required)

            ) * 100,

            2

        )

    elif specialized_preferred:

        specialized_keyword_score = round(

            (

                len(matched_specialized_preferred)

                /

                len(specialized_preferred)

            ) * 100,

            2

        )

    else:

        specialized_keyword_score = 100.0

    total_preferred = specialized_preferred

    matched_all_preferred = (
        matched_specialized_preferred
    )

    if total_preferred:

        preferred_keyword_score = round(

            (

                len(matched_all_preferred)

                /

                len(total_preferred)

            ) * 100,

            2

        )

    else:

        preferred_keyword_score = 100.0

    if soft_required:

        soft_skill_score = round(

            (

                len(matched_soft)

                /

                len(soft_required)

            ) * 100,

            2

        )

    else:

        soft_skill_score = 100.0

    try:

        evidence_analysis = verify_skill_evidence(

            extracted_text,

            required_skills,

            preferred_skills

        )

    except Exception:

        evidence_analysis = {

            "results": [],
            "evidence_score": 0.0,
            "required_evidence_score": 0.0,
            "preferred_evidence_score": 0.0,
            "matched": [],
            "missing": [],
            "required_matched": [],
            "preferred_matched": [],
            "required_missing": [],
            "preferred_missing": [],
            "sections": {}

        }

    evidence_results = evidence_analysis.get(
        "results",
        []
    )

    technical_evidence_score = (

        calculate_evidence_category_score(

            evidence_results,

            technical_required,

            "Required"

        )

    )

    specialized_evidence_score = (

        calculate_evidence_category_score(

            evidence_results,

            specialized_required,

            "Required"

        )

    )

    preferred_evidence_score = (

        calculate_evidence_category_score(

            evidence_results,

            total_preferred,

            "Preferred"

        )

    )

    technical_score = blend_keyword_and_evidence(

        technical_keyword_score,

        technical_evidence_score,

        0.35

    )

    specialized_score = blend_keyword_and_evidence(

        specialized_keyword_score,

        specialized_evidence_score,

        0.40

    )

    preferred_score = blend_keyword_and_evidence(

        preferred_keyword_score,

        preferred_evidence_score,

        0.25

    )

    try:

        jd_education = extract_education_requirements(

            job_description

        )

    except Exception:

        jd_education = {}

    try:

        resume_education = extract_resume_education(

            extracted_text

        )

    except Exception:

        resume_education = {}

    try:

        education_score, education_checks = (

            calculate_education_score(

                jd_education,

                resume_education

            )

        )

    except Exception:

        education_score = 0.0

        education_checks = [

            "Education could not be evaluated."

        ]

    try:

        (

            project_score,

            project_evidence,

            project_details

        ) = calculate_project_evidence_score(

            extracted_text,

            job_description

        )

    except Exception:

        project_score = 0.0

        project_evidence = []

        project_details = {}

    improved_project = (

        calculate_improved_project_relevance(

            extracted_text,

            job_description,

            required_skills,

            preferred_skills

        )

    )

    project_score = max(

        float(project_score),

        float(

            improved_project.get(
                "score",
                0
            )

        )

    )

    project_evidence = list(

        project_evidence or []

    )

    project_evidence.extend(

        improved_project.get(
            "evidence",
            []
        )

    )

    project_details = {

        **(

            project_details

            if isinstance(
                project_details,
                dict
            )

            else {}

        ),

        "improved_relevance":
            improved_project

    }

    if project_score >= 80:

        project_relevance = "Strong"

    elif project_score >= 60:

        project_relevance = "Good"

    elif project_score >= 40:

        project_relevance = "Moderate"

    else:

        project_relevance = "Low"

    technical_contribution = round(

        technical_score * 0.35,

        2

    )

    specialized_contribution = round(

        specialized_score * 0.25,

        2

    )

    preferred_contribution = round(

        preferred_score * 0.10,

        2

    )

    soft_skill_contribution = round(

        soft_skill_score * 0.05,

        2

    )

    education_contribution = round(

        education_score * 0.15,

        2

    )

    project_contribution = round(

        project_score * 0.10,

        2

    )

    overall_score = round(

        technical_contribution

        +

        specialized_contribution

        +

        preferred_contribution

        +

        soft_skill_contribution

        +

        education_contribution

        +

        project_contribution,

        2

    )

    if overall_score >= 80:

        recommendation = "Strong Match"

    elif overall_score >= 65:

        recommendation = "Good Match"

    elif overall_score >= 50:

        recommendation = "Moderate Match"

    else:

        recommendation = "Low Match"

    proficiency = {}

    for skill in sorted(

        resume_skills,

        key=str

    ):

        try:

            proficiency[skill] = detect_proficiency(

                extracted_text,

                skill

            )

        except Exception:

            proficiency[skill] = "Not determined"

    strengths = set()

    strengths.update(
        matched_technical
    )

    strengths.update(
        matched_specialized_required
    )

    strengths.update(
        matched_specialized_preferred
    )

    strengths.update(
        matched_preferred
    )

    strengths.update(
        matched_soft
    )

    strengths.update(

        evidence_analysis.get(
            "required_matched",
            []
        )

    )

    gaps = set()

    gaps.update(
        missing_technical
    )

    gaps.update(
        missing_specialized_required
    )

    gaps.update(
        missing_specialized_preferred
    )

    gaps.update(
        missing_preferred
    )

    gaps.update(
        missing_soft
    )

    gaps.update(

        evidence_analysis.get(
            "required_missing",
            []
        )

    )

    candidate_result = {

        "filename":
            filename,

        "overall_score":
            overall_score,

        "recommendation":
            recommendation,

        "technical_score":
            technical_score,

        "specialized_score":
            specialized_score,

        "preferred_score":
            preferred_score,

        "soft_skill_score":
            soft_skill_score,

        "education_score":
            education_score,

        "project_score":
            project_score,

        "project_relevance":
            project_relevance,

        "similarity_score":
            similarity_score,

        "technical_keyword_score":
            technical_keyword_score,

        "specialized_keyword_score":
            specialized_keyword_score,

        "preferred_keyword_score":
            preferred_keyword_score,

        "technical_evidence_score":
            technical_evidence_score,

        "specialized_evidence_score":
            specialized_evidence_score,

        "evidence_score":
            evidence_analysis.get(
                "evidence_score",
                0
            ),

        "required_evidence_score":
            evidence_analysis.get(
                "required_evidence_score",
                0
            ),

        "preferred_evidence_score":
            preferred_evidence_score,

        "technical_contribution":
            technical_contribution,

        "specialized_contribution":
            specialized_contribution,

        "preferred_contribution":
            preferred_contribution,

        "soft_skill_contribution":
            soft_skill_contribution,

        "education_contribution":
            education_contribution,

        "project_contribution":
            project_contribution,

        "resume_skills":
            resume_skills,

        "jd_skills":
            jd_skills,

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "technical_required":
            technical_required,

        "specialized_skills":
            specialized_required
            |
            specialized_preferred,

        "specialized_required":
            specialized_required,

        "specialized_preferred":
            specialized_preferred,

        "soft_required":
            soft_required,

        "matched_technical":
            matched_technical,

        "missing_technical":
            missing_technical,

        "matched_specialized_required":
            matched_specialized_required,

        "missing_specialized_required":
            missing_specialized_required,

        "matched_specialized_preferred":
            matched_specialized_preferred,

        "missing_specialized_preferred":
            missing_specialized_preferred,

        "matched_preferred":
            matched_preferred,

        "missing_preferred":
            missing_preferred,

        "matched_soft":
            matched_soft,

        "missing_soft":
            missing_soft,

        "proficiency":
            proficiency,

        "strengths":
            strengths,

        "gaps":
            gaps,

        "jd_education":
            jd_education,

        "resume_education":
            resume_education,

        "education_checks":
            education_checks,

        "project_evidence":
            project_evidence,

        "project_details":
            project_details,

        "improved_project":
            improved_project,

        "evidence_results":
            evidence_results,

        "evidence_sections":
            evidence_analysis.get(
                "sections",
                {}
            ),

        "evidence_matched":
            evidence_analysis.get(
                "matched",
                []
            ),

        "evidence_missing":
            evidence_analysis.get(
                "missing",
                []
            ),

        "required_evidence_matched":
            evidence_analysis.get(
                "required_matched",
                []
            ),

        "required_evidence_missing":
            evidence_analysis.get(
                "required_missing",
                []
            ),

        "preferred_evidence_matched":
            evidence_analysis.get(
                "preferred_matched",
                []
            ),

        "preferred_evidence_missing":
            evidence_analysis.get(
                "preferred_missing",
                []
            ),

        "jd_analysis":
            jd_analysis,

        "cleaned_resume":
            cleaned_resume,

        "cleaned_jd":
            cleaned_jd

    }

    ai_review_data = generate_ai_candidate_review(
        candidate_result
    )

    candidate_result["ai_review"] = (
        ai_review_data["review"]
    )

    candidate_result["gemini_analysis"] = None
    candidate_result["gemini_status"] = "not_requested"
    candidate_result["gemini_model"] = None
    candidate_result["gemini_error"] = None
    candidate_result["gemini_resume_text"] = extracted_text
    candidate_result["gemini_job_description"] = job_description

    candidate_result["final_decision"] = (
        ai_review_data["final_decision"]
    )

    candidate_result["selection_reason"] = (
        ai_review_data["selection_reason"]
    )

    candidate_result["not_selection_reason"] = (
        ai_review_data["not_selection_reason"]
    )

    candidate_result["ai_matched_skills"] = (
        ai_review_data["matched_skills"]
    )

    candidate_result["ai_missing_skills"] = (
        ai_review_data["missing_skills"]
    )

    return candidate_result


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/upload",
    methods=["POST"]
)
def upload_resumes():

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    upload_mode = request.form.get(
        "upload_mode",
        "single"
    )

    if not job_description:

        return """

        <h2>Job description is required.</h2>

        <a href="/">Go back</a>

        """

    if upload_mode == "multiple":

        files = request.files.getlist(
            "resume_folder"
        )

    else:

        files = request.files.getlist(
            "resume"
        )

    if not files:

        files = request.files.getlist(
            "resumes"
        )

    valid_files = []

    for file in files:

        if not file:
            continue

        if not file.filename:
            continue

        filename = os.path.basename(
            file.filename
        )

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension in SUPPORTED_EXTENSIONS:

            valid_files.append(
                file
            )

    if not valid_files:

        return """

        <h2>No supported resumes were selected.</h2>

        <p>
            Please select at least one resume.
        </p>

        <p>
            Supported formats:
            PDF, DOCX, DOC, TXT, JPG, JPEG, PNG
        </p>

        <a href="/">Go back</a>

        """

    batch_id = str(
        uuid.uuid4()
    )[:8]

    batch_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        batch_id
    )

    os.makedirs(
        batch_folder,
        exist_ok=True
    )

    candidates = []

    used_names = set()

    for index, file in enumerate(
        valid_files,
        start=1
    ):

        original_filename = os.path.basename(
            file.filename
        )

        name, extension = os.path.splitext(
            original_filename
        )

        safe_filename = original_filename

        counter = 1

        while safe_filename in used_names:

            safe_filename = (
                f"{name}_{counter}{extension}"
            )

            counter += 1

        used_names.add(
            safe_filename
        )

        file_path = os.path.join(
            batch_folder,
            safe_filename
        )

        try:

            file.save(
                file_path
            )

            print(

                f"[{index}/{len(valid_files)}] "
                f"Processing: {original_filename}"

            )

            result = analyze_candidate(

                file_path,

                original_filename,

                job_description

            )

            candidates.append(
                result
            )

            if "overall_score" in result:

                print(

                    f"Score: "
                    f"{result['overall_score']}%"

                )

            else:

                print(

                    f"Error: "
                    f"{result.get('error', 'Unknown error')}"

                )

        except Exception as e:

            candidates.append({

                "filename":
                    original_filename,

                "error":
                    f"File processing failed: {str(e)}"

            })

    valid_candidates = [

        candidate

        for candidate in candidates

        if "overall_score" in candidate

    ]

    invalid_candidates = [

        candidate

        for candidate in candidates

        if "overall_score" not in candidate

    ]

    valid_candidates.sort(

        key=lambda candidate:
            candidate["overall_score"],

        reverse=True

    )

    for index, candidate in enumerate(

        valid_candidates,

        start=1

    ):

        candidate["rank"] = index

    app.config["LAST_RESULTS"] = {

        candidate["rank"]:
            candidate

        for candidate in valid_candidates

    }

    if not valid_candidates:

        error_html = ""

        for candidate in invalid_candidates:

            error_html += f"""

            <li>

                <strong>
                    {escape(candidate["filename"])}
                </strong>

                -

                {escape(

                    candidate.get(
                        "error",
                        "Unknown error"
                    )

                )}

            </li>

            """

        return f"""

        <!DOCTYPE html>

        <html>

        <head>

            <title>
                Screening Error
            </title>

            <style>

                body {{

                    font-family:
                        Arial, sans-serif;

                    background:
                        #f4f6fa;

                    padding:
                        40px;

                }}

                .box {{

                    max-width:
                        800px;

                    margin:
                        auto;

                    background:
                        white;

                    padding:
                        30px;

                    border-radius:
                        12px;

                }}

                a {{

                    display:
                        inline-block;

                    margin-top:
                        20px;

                    padding:
                        10px 16px;

                    background:
                        #111827;

                    color:
                        white;

                    text-decoration:
                        none;

                    border-radius:
                        8px;

                }}

            </style>

        </head>

        <body>

            <div class="box">

                <h1>
                    No resumes could be analyzed
                </h1>

                <ul>

                    {error_html}

                </ul>

                <a href="/">
                    Try Again
                </a>

            </div>

        </body>

        </html>

        """

    return render_ranking_page(

        valid_candidates,

        invalid_candidates

    )


def render_ranking_page(
    valid_candidates,
    invalid_candidates
):

    ranking_rows = ""

    for candidate in valid_candidates:

        recommendation_class = (

            candidate["recommendation"]
            .lower()
            .replace(
                " ",
                "-"
            )

        )

        ranking_rows += f"""

        <tr>

            <td>

                <strong>
                    #{candidate["rank"]}
                </strong>

            </td>

            <td>

                <a href="/candidate/{candidate["rank"]}">

                    {escape(
                        candidate["filename"]
                    )}

                </a>

            </td>

            <td>

                <strong>
                    {candidate["overall_score"]}%
                </strong>

            </td>

            <td>
                {candidate["technical_score"]}%
            </td>

            <td>
                {candidate["specialized_score"]}%
            </td>

            <td>
                {candidate["preferred_score"]}%
            </td>

            <td>
                {candidate["soft_skill_score"]}%
            </td>

            <td>
                {candidate["education_score"]}%
            </td>

            <td>
                {candidate["project_score"]}%
            </td>

            <td>
                {candidate["evidence_score"]}%
            </td>

            <td>

                <span class="recommendation {recommendation_class}">

                    {escape(
                        candidate["recommendation"]
                    )}

                </span>

            </td>

            <td>

                <a href="/candidate/{candidate["rank"]}">
                    View Details
                </a>

            </td>

        </tr>

        """

    failed_html = ""

    if invalid_candidates:

        failed_items = ""

        for candidate in invalid_candidates:

            failed_items += f"""

            <li>

                <strong>
                    {escape(candidate["filename"])}
                </strong>

                -

                {escape(

                    candidate.get(
                        "error",
                        "Unknown error"
                    )

                )}

            </li>

            """

        failed_html = f"""

        <section class="failed">

            <h3>
                Files that could not be analyzed
            </h3>

            <ul>

                {failed_items}

            </ul>

        </section>

        """

    top_candidate = valid_candidates[0]

    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>
            Candidate Ranking
        </title>

        <style>

            * {{

                box-sizing:
                    border-box;

            }}

            body {{

                margin:
                    0;

                padding:
                    30px;

                font-family:
                    Arial, sans-serif;

                background:
                    #f4f6fa;

                color:
                    #172033;

            }}

            .container {{

                width:
                    min(1500px, 100%);

                margin:
                    auto;

            }}

            .header {{

                background:
                    white;

                padding:
                    28px;

                border-radius:
                    16px;

                border:
                    1px solid #e3e7ee;

                margin-bottom:
                    20px;

            }}

            h1 {{

                margin:
                    0 0 8px;

            }}

            .summary {{

                display:
                    grid;

                grid-template-columns:
                    repeat(4, minmax(0, 1fr));

                gap:
                    14px;

                margin-top:
                    20px;

            }}

            .summary-card {{

                background:
                    white;

                border:
                    1px solid #e2e6ed;

                border-radius:
                    12px;

                padding:
                    20px;

            }}

            .summary-card strong {{

                display:
                    block;

                font-size:
                    28px;

                margin-top:
                    5px;

            }}

            .table-wrapper {{

                overflow-x:
                    auto;

                background:
                    white;

                border-radius:
                    14px;

                border:
                    1px solid #e2e6ed;

            }}

            table {{

                width:
                    100%;

                border-collapse:
                    collapse;

                min-width:
                    1250px;

            }}

            th,
            td {{

                padding:
                    14px;

                border-bottom:
                    1px solid #edf0f4;

                text-align:
                    left;

                font-size:
                    13px;

            }}

            th {{

                background:
                    #f8fafc;

            }}

            a {{

                color:
                    #111827;

                font-weight:
                    700;

                text-decoration:
                    none;

            }}

            .recommendation {{

                display:
                    inline-block;

                padding:
                    6px 9px;

                border-radius:
                    7px;

                background:
                    #eef1f5;

                font-weight:
                    700;

            }}

            .failed {{

                margin-top:
                    20px;

                background:
                    white;

                padding:
                    20px;

                border-radius:
                    14px;

                border:
                    1px solid #e2e6ed;

            }}

            .actions {{

                margin-top:
                    20px;

            }}

            .button {{

                display:
                    inline-block;

                padding:
                    11px 17px;

                border-radius:
                    8px;

                background:
                    #111827;

                color:
                    white;

                margin-right:
                    8px;

            }}

            @media(max-width: 800px) {{

                body {{

                    padding:
                        15px;

                }}

                .summary {{

                    grid-template-columns:
                        1fr 1fr;

                }}

            }}

        </style>

    </head>

    <body>

        <main class="container">

            <section class="header">

                <h1>
                    AI Resume Screening Results
                </h1>

                <p>

                    Candidates are ranked using
                    technical skills, specialized
                    requirements, preferred skills,
                    soft skills, education, project
                    relevance and evidence-based
                    skill verification.

                </p>

            </section>

            <section class="summary">

                <div class="summary-card">

                    Candidates

                    <strong>
                        {len(valid_candidates)}
                    </strong>

                </div>

                <div class="summary-card">

                    Top Score

                    <strong>
                        {top_candidate["overall_score"]}%
                    </strong>

                </div>

                <div class="summary-card">

                    Top Candidate

                    <strong>
                        #{top_candidate["rank"]}
                    </strong>

                </div>

                <div class="summary-card">

                    Evidence

                    <strong>
                        {top_candidate["evidence_score"]}%
                    </strong>

                </div>

            </section>

            <section style="margin-top:20px">

                <div class="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Rank
                                </th>

                                <th>
                                    Resume
                                </th>

                                <th>
                                    Overall
                                </th>

                                <th>
                                    Technical
                                </th>

                                <th>
                                    Specialized
                                </th>

                                <th>
                                    Preferred
                                </th>

                                <th>
                                    Soft Skills
                                </th>

                                <th>
                                    Education
                                </th>

                                <th>
                                    Projects
                                </th>

                                <th>
                                    Evidence
                                </th>

                                <th>
                                    Recommendation
                                </th>

                                <th>
                                    Action
                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            {ranking_rows}

                        </tbody>

                    </table>

                </div>

            </section>

            {failed_html}

            <div class="actions">

                <a
                    class="button"
                    href="/"
                >

                    Screen New Resumes

                </a>

            </div>

        </main>

    </body>

    </html>

    """


@app.route("/ranking")
def ranking_page():

    results = app.config.get(
        "LAST_RESULTS",
        {}
    )

    if not results:

        return """

        <h2>
            No ranking results are available.
        </h2>

        <p>
            Please screen resumes first.
        </p>

        <a href="/">
            Go to Screening
        </a>

        """

    valid_candidates = sorted(

        results.values(),

        key=lambda candidate:
            candidate.get(
                "rank",
                0
            )

    )

    return render_ranking_page(

        valid_candidates,

        []

    )


def render_candidate_page(candidate):

    proficiency_rows = ""

    for skill, level in sorted(

        candidate.get(
            "proficiency",
            {}
        ).items(),

        key=lambda item:
            str(item[0])

    ):

        proficiency_rows += f"""

        <tr>

            <td>

                {escape(
                    str(skill).title()
                )}

            </td>

            <td>

                {escape(
                    str(level)
                )}

            </td>

        </tr>

        """

    project_rows = ""

    improved_project = candidate.get(
        "improved_project",
        {}
    )

    improved_details = improved_project.get(
        "details",
        {}
    )

    required_matches = improved_details.get(
        "required_matches",
        []
    )

    preferred_matches = improved_details.get(
        "preferred_matches",
        []
    )

    required_total = max(

        len(

            candidate.get(
                "required_skills",
                []
            )

        ),

        1

    )

    preferred_total = max(

        len(

            candidate.get(
                "preferred_skills",
                []
            )

        ),

        1

    )

    required_project_coverage = round(

        (

            len(required_matches)

            /

            required_total

        ) * 100,

        2

    )

    preferred_project_coverage = round(

        (

            len(preferred_matches)

            /

            preferred_total

        ) * 100,

        2

    )

    project_rows += f"""

    <tr>

        <td>
            Required Skill Coverage
        </td>

        <td>
            Project Evidence
        </td>

        <td>
            {required_project_coverage}%
        </td>

    </tr>

    <tr>

        <td>
            Preferred Skill Coverage
        </td>

        <td>
            Project Evidence
        </td>

        <td>
            {preferred_project_coverage}%
        </td>

    </tr>

    <tr>

        <td>
            Implementation Evidence
        </td>

        <td>
            Project Description
        </td>

        <td>

            {improved_details.get(
                "implementation_count",
                0
            )}

        </td>

    </tr>

    <tr>

        <td>
            Overall Project Relevance
        </td>

        <td>

            {escape(

                str(

                    improved_project.get(

                        "label",

                        candidate.get(
                            "project_relevance",
                            "Low"
                        )

                    )

                )

            )}

        </td>

        <td>
            {candidate["project_score"]}%
        </td>

    </tr>

    """

    evidence_rows = ""

    for item in candidate.get(

        "evidence_results",

        []

    ):

        skill = escape(

            str(

                item.get(
                    "skill",
                    ""
                )

            ).title()

        )

        requirement_type = escape(

            str(

                item.get(
                    "requirement_type",
                    ""
                )

            )

        )

        strength = escape(

            str(

                item.get(
                    "strength",
                    "No Evidence"
                )

            )

        )

        score = item.get(
            "score",
            0
        )

        sources = item.get(
            "sources",
            []
        )

        source_text = ", ".join(

            str(source)

            for source in sources

        )

        if not source_text:

            source_text = (
                "No supporting section"
            )

        status = (

            "Supported"

            if item.get(
                "matched",
                False
            )

            else

            "Not Demonstrated"

        )

        evidence_rows += f"""

        <tr>

            <td>
                {skill}
            </td>

            <td>
                {requirement_type}
            </td>

            <td>
                {escape(status)}
            </td>

            <td>
                {strength}
            </td>

            <td>
                {score}%
            </td>

            <td>
                {escape(source_text)}
            </td>

        </tr>

        """

    if not evidence_rows:

        evidence_rows = """

        <tr>

            <td colspan="6">

                No detailed evidence records available.

            </td>

        </tr>

        """

    project_evidence_html = make_list(

        candidate.get(
            "project_evidence",
            []
        )

    )

    education_checks_html = make_list(

        candidate.get(
            "education_checks",
            []
        )

    )

    technical_matched_html = make_list(

        candidate.get(
            "matched_technical",
            []
        )

    )

    technical_missing_html = make_list(

        candidate.get(
            "missing_technical",
            []
        )

    )

    specialized_matched_html = make_list(

        candidate.get(
            "matched_specialized_required",
            []
        )

    )

    specialized_missing_html = make_list(

        candidate.get(
            "missing_specialized_required",
            []
        )

    )

    preferred_matched_html = make_list(

        candidate.get(
            "matched_preferred",
            []
        )

    )

    preferred_missing_html = make_list(

        candidate.get(
            "missing_preferred",
            []
        )

    )

    soft_matched_html = make_list(

        candidate.get(
            "matched_soft",
            []
        )

    )

    soft_missing_html = make_list(

        candidate.get(
            "missing_soft",
            []
        )

    )

    strengths_html = make_strength_list(

        candidate.get(
            "strengths",
            []
        )

    )

    gaps_html = make_gap_list(

        candidate.get(
            "gaps",
            []
        )

    )

    specialized_section = make_list(

        candidate.get(
            "specialized_skills",
            []
        )

    )

    evidence_summary = ""

    try:

        evidence_summary = get_evidence_summary(

            candidate.get(
                "evidence_results",
                []
            )

        )

    except Exception:

        evidence_summary = (
            "Evidence summary unavailable."
        )

    return render_template(

        "candidate.html",

        candidate=candidate,

        technical_matched_html=
            technical_matched_html,

        technical_missing_html=
            technical_missing_html,

        specialized_matched_html=
            specialized_matched_html,

        specialized_missing_html=
            specialized_missing_html,

        preferred_matched_html=
            preferred_matched_html,

        preferred_missing_html=
            preferred_missing_html,

        soft_matched_html=
            soft_matched_html,

        soft_missing_html=
            soft_missing_html,

        strengths_html=
            strengths_html,

        gaps_html=
            gaps_html,

        education_checks_html=
            education_checks_html,

        project_evidence_html=
            project_evidence_html,

        proficiency_rows=
            proficiency_rows,

        project_rows=
            project_rows,

        evidence_rows=
            evidence_rows,

        evidence_summary=
            evidence_summary,

        ai_review=
            candidate.get(
                "ai_review",
                "AI candidate review is unavailable."
            ),

        gemini_analysis=
            candidate.get("gemini_analysis"),

        gemini_error=
            candidate.get("gemini_error"),

        gemini_status=
            candidate.get("gemini_status", "unavailable"),

        gemini_model=
            candidate.get("gemini_model"),

        final_decision=
            candidate.get(
                "final_decision",
                "Decision unavailable."
            ),

        selection_reason=
            candidate.get(
                "selection_reason",
                "Selection reason unavailable."
            ),

        not_selection_reason=
            candidate.get(
                "not_selection_reason",
                "Reason unavailable."
            ),

        specialized_section=
            specialized_section

    )


@app.route(
    "/candidate/<int:rank>"
)
def candidate_details(rank):

    candidate = app.config[
        "LAST_RESULTS"
    ].get(rank)

    if not candidate:

        return """

        <h2>
            Candidate not found.
        </h2>

        <a href="/">
            Back
        </a>

        """

    return render_candidate_page(
        candidate
    )


@app.route("/candidate/<int:rank>/gemini", methods=["POST"])
def run_candidate_gemini(rank):
    candidate = app.config["LAST_RESULTS"].get(rank)

    if candidate is None:
        return "Candidate not found", 404

    if candidate.get("gemini_status") == "success":
        return render_candidate_page(candidate)

    resume_text = candidate.get("gemini_resume_text", "")
    job_description = candidate.get("gemini_job_description", "")

    if not resume_text or not job_description:
        candidate["gemini_status"] = "failed"
        candidate["gemini_error"] = "Resume text or job description is missing."
        return render_candidate_page(candidate)

    try:
        result = analyze_resume_with_gpt(resume_text, job_description)
        if not isinstance(result, dict):
            raise ValueError("Gemini returned an unexpected response.")

        candidate["gemini_status"] = result.get("status", "failed")
        candidate["gemini_analysis"] = (
            result.get("analysis")
            if candidate["gemini_status"] == "success"
            else None
        )
        candidate["gemini_model"] = result.get("model")
        candidate["gemini_error"] = (
            None if candidate["gemini_status"] == "success"
            else "Gemini is temporarily unavailable. Candidate scores and rankings remain available."
        )
    except Exception as error:
        app.logger.warning("Gemini analysis failed: %s", error)
        candidate["gemini_status"] = "failed"
        candidate["gemini_analysis"] = None
        candidate["gemini_error"] = (
            "Gemini is temporarily unavailable. Candidate scores and rankings remain available."
        )

    return render_candidate_page(candidate)


if __name__ == "__main__":

    app.run(
        debug=True
    )