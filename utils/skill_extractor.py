
import re


SKILL_PATTERNS = {
    "python": r"\bpython\b",
    "java": r"\bjava\b",
    "javascript": r"\bjavascript\b|\bjava\s+script\b",
    "c": r"(?<![a-z+#])c(?![a-z+#])",
    "c++": r"\bc\s*\+\s*\+|\bcpp\b|c plus plus",
    "c#": r"\bc\s*#|\bcsharp\b|c sharp",
    "typescript": r"\btypescript\b",
    "kotlin": r"\bkotlin\b",
    "php": r"\bphp\b",
    "ruby": r"\bruby\b",
    "golang": r"\bgolang\b|\bgo language\b",
    "html": r"\bhtml5?\b",
    "css": r"\bcss3?\b",
    "react": r"\breact(?:\s*\.?\s*js)?\b",
    "angular": r"\bangular\b",
    "vue": r"\bvue(?:\s*\.?\s*js)?\b",
    "node.js": r"\bnode(?:\s*\.?\s*js|js)\b",
    "express.js": r"\bexpress(?:\s*\.?\s*js|js)\b",
    "django": r"\bdjango\b",
    "flask": r"\bflask\b",
    "spring boot": r"\bspring\s+boot\b",
    "bootstrap": r"\bbootstrap\b",
    "tailwind css": r"\btailwind(?:\s+css)?\b",
    "rest api": r"\brest(?:ful)?\s+apis?\b|\brestful\b",
    "graphql": r"\bgraphql\b",
    "sql": r"\bsql\b",
    "mysql": r"\bmysql\b",
    "postgresql": r"\bpostgresql\b|\bpostgres\b",
    "mongodb": r"\bmongodb\b|\bmongo\s+db\b",
    "sqlite": r"\bsqlite\b",
    "oracle": r"\boracle\b",
    "sql server": r"\bsql\s+server\b",
    "database": r"\bdatabases?\b",
    "nosql": r"\bnosql\b",
    "object oriented programming": r"\bobject[\s-]+oriented[\s-]+programming\b|\boop\b",
    "data structures": r"\bdata[\s-]+structures?\b",
    "algorithms": r"\balgorithms?\b",
    "problem solving": r"\bproblem[\s-]+solving\b",
    "analytical skills": r"\banalytical\s+skills?\b",
    "analytical thinking": r"\banalytical\s+thinking\b",
    "debugging": r"\bdebugging\b|\bdebug\b",
    "software testing": r"\bsoftware\s+testing\b",
    "unit testing": r"\bunit\s+testing\b",
    "integration testing": r"\bintegration\s+testing\b",
    "software development": r"\bsoftware\s+development\b",
    "software engineering": r"\bsoftware\s+engineering\b",
    "software development life cycle": r"\bsoftware\s+development\s+life\s+cycle\b|\bsdlc\b",
    "artificial intelligence": r"\bartificial\s+intelligence\b",
    "machine learning": r"\bmachine\s+learning\b",
    "deep learning": r"\bdeep\s+learning\b",
    "natural language processing": r"\bnatural\s+language\s+processing\b|\bnlp\b",
    "computer vision": r"\bcomputer\s+vision\b",
    "neural networks": r"\bneural\s+networks?\b",
    "generative ai": r"\bgenerative\s+ai\b|\bgenai\b",
    "data science": r"\bdata\s+science\b",
    "data analytics": r"\bdata\s+analytics\b",
    "big data": r"\bbig\s+data\b",
    "data visualization": r"\bdata\s+visualization\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "keras": r"\bkeras\b",
    "scikit learn": r"\bscikit[\s-]+learn\b|\bsklearn\b",
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "opencv": r"\bopencv\b|\bopen\s*cv\b",
    "git": r"\bgit\b",
    "github": r"\bgithub\b",
    "gitlab": r"\bgitlab\b",
    "version control": r"\bversion\s+control\b",
    "aws": r"\baws\b|\bamazon\s+web\s+services\b",
    "microsoft azure": r"\bazure\b|\bmicrosoft\s+azure\b",
    "google cloud": r"\bgoogle\s+cloud\b|\bgcp\b",
    "oracle cloud": r"\boracle\s+cloud\b",
    "cloud computing": r"\bcloud\s+computing\b",
    "cloud": r"\bcloud\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes\b|\bk8s\b",
    "linux": r"\blinux\b",
    "ci/cd": r"\bci\s*/\s*cd\b|\bcontinuous\s+integration\b|\bcontinuous\s+deployment\b",
    "apache spark": r"\bapache\s+spark\b|\bspark\b",
    "hadoop": r"\bhadoop\b",
    "power bi": r"\bpower\s+bi\b",
    "tableau": r"\btableau\b",
    "excel": r"\bexcel\b",
    "microsoft 365": r"\bmicrosoft\s+365\b|\bm365\b",
    "sharepoint": r"\bsharepoint\b",
    "power apps": r"\bpower\s+apps?\b|\bpowerapps\b",
    "power automate": r"\bpower\s+automate\b",
    "power platform": r"\bpower\s+platform\b",
    "agile": r"\bagile\b",
    "scrum": r"\bscrum\b",
    "kanban": r"\bkanban\b",
    "communication": r"\bcommunication(?:\s+skills?)?\b",
    "leadership": r"\bleadership\b",
    "teamwork": r"\bteamwork\b|\bteam\s+work\b",
    "collaboration": r"\bcollaboration\b|\bcollaborative\b",
    "interpersonal skills": r"\binterpersonal\s+skills?\b",
    "time management": r"\btime\s+management\b",
    "critical thinking": r"\bcritical\s+thinking\b",
    "adaptability": r"\badaptability\b|\badaptable\b",
    "decision making": r"\bdecision[\s-]+making\b",
    "creativity": r"\bcreativity\b|\bcreative\b",
    "presentation skills": r"\bpresentation\s+skills?\b",
    "content moderation": r"\bcontent\s+moderation\b|\bcontent\s+moderator\b",
    "content classification": r"\bcontent\s+classification\b|\bclassify\s+content\b|\bclassifying\s+content\b",
    "content review": r"\bcontent\s+review\b|\breview(?:ing)?\s+(?:of\s+)?content\b",
    "policy compliance": r"\bpolicy\s+compliance\b|\bclient\s+policies\b|\bclient\s+guidelines\b",
    "attention to detail": r"\battention\s+to\s+detail\b",
    "emotional resilience": r"\bemotional\s+resilience\b|\bresilience\b",
    "stress management": r"\bstress[\s-]+management\b",
    "comprehension": r"\bcomprehension\b",
    "objectivity": r"\bobjectively\b|\bobjectivity\b",
    "investigation": r"\binvestigat(?:e|es|ed|ing|ion)\b",
    "issue resolution": r"\bresolve\s+issues\b|\bissue\s+resolution\b",
    "content analysis": r"\b(?:analy[sz](?:e|es|ed|ing|is|ation)|analyzing)\s+(?:user\s+)?content\b",
    "information analysis": r"\b(?:analy[sz](?:e|es|ed|ing|is)|analyzing)\s+information\b",
    "judgment": r"\bjudg(?:e)?ments?\b",
    "risk assessment": r"\brisk\s+assessment\b",
    "quality assurance": r"\bquality\s+assurance\b",
    "cybersecurity": r"\bcyber\s*security\b|\bcybersecurity\b",
    "blockchain": r"\bblockchain\b",
    "internet of things": r"\binternet\s+of\s+things\b|\biot\b",
    "robotics": r"\brobotics\b"
}


SKILL_ALIASES = {
    "oop": "object oriented programming",
    "object-oriented programming": "object oriented programming",
    "problem-solving": "problem solving",
    "ml": "machine learning",
    "nlp": "natural language processing",
    "restful api": "rest api",
    "nodejs": "node.js",
    "node js": "node.js",
    "expressjs": "express.js",
    "express js": "express.js",
    "scikit-learn": "scikit learn",
    "sklearn": "scikit learn",
    "mongo db": "mongodb",
    "powerapps": "power apps",
    "m365": "microsoft 365",
    "gcp": "google cloud",
    "k8s": "kubernetes",
    "sdlc": "software development life cycle",
    "cpp": "c++",
    "c plus plus": "c++",
    "cyber security": "cybersecurity",
    "iot": "internet of things",
    "content moderator": "content moderation",
    "review of content": "content review",
    "decision-making": "decision making"
}


STRONG_WORDS = [
    "expert", "expertise", "proficient", "proficiency",
    "advanced", "specialist", "extensive experience",
    "deep knowledge", "strong knowledge", "highly skilled"
]

PRACTICAL_WORDS = [
    "developed", "built", "implemented", "designed",
    "created", "engineered", "deployed", "integrated",
    "configured", "automated", "optimized", "programmed",
    "maintained", "hands on", "practical experience",
    "practical knowledge"
]

INTERMEDIATE_WORDS = [
    "intermediate", "working knowledge", "good knowledge",
    "good understanding", "solid knowledge",
    "solid understanding", "competent"
]

FAMILIAR_WORDS = [
    "familiar", "familiarity", "basic", "beginner",
    "learning", "currently studying", "basic knowledge",
    "basic understanding", "exposure to"
]


def normalize_text(text):
    text = str(text or "").lower()

    replacements = {
        "object-oriented": "object oriented",
        "object–oriented": "object oriented",
        "problem-solving": "problem solving",
        "problem–solving": "problem solving",
        "hands-on": "hands on",
        "hands–on": "hands on",
        "powerapps": "power apps",
        "m365": "microsoft 365",
        "nodejs": "node.js",
        "node js": "node.js",
        "expressjs": "express.js",
        "express js": "express.js",
        "scikit-learn": "scikit learn",
        "sklearn": "scikit learn",
        "c plus plus": "c++",
        "cyber security": "cybersecurity",
        "decision-making": "decision making"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"\s+", " ", text).strip()


def canonicalize_skill(skill):
    skill = normalize_text(skill)
    return SKILL_ALIASES.get(skill, skill)


def get_skill_pattern(skill):
    skill = canonicalize_skill(skill)

    if skill in SKILL_PATTERNS:
        return SKILL_PATTERNS[skill]

    escaped = re.escape(skill).replace(r"\ ", r"\s+")
    return rf"(?<!\w){escaped}(?!\w)"


def skill_present(text, skill):
    normalized = normalize_text(text)

    try:
        return bool(
            re.search(
                get_skill_pattern(skill),
                normalized,
                re.IGNORECASE
            )
        )
    except re.error:
        return False


def extract_skills(text):
    normalized = normalize_text(text)
    detected = set()

    for skill, pattern in SKILL_PATTERNS.items():
        try:
            if re.search(pattern, normalized, re.IGNORECASE):
                detected.add(skill)
        except re.error:
            continue

    return sorted(detected)


def extract_skill_sections(job_description):
    text = normalize_text(job_description)

    required_skills = set()
    preferred_skills = set()

    sentences = re.split(r"[\n;.!]+", text)

    required_cues = [
        "required", "must have", "must possess",
        "mandatory", "essential", "minimum qualification",
        "minimum requirement", "need to have",
        "you will need", "should have"
    ]

    preferred_cues = [
        "preferred", "desirable", "nice to have",
        "good to have", "bonus", "ideally",
        "optional", "familiarity with",
        "would be an advantage"
    ]

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        skills = set(extract_skills(sentence))

        if not skills:
            continue

        is_preferred = any(
            cue in sentence for cue in preferred_cues
        )

        is_required = any(
            cue in sentence for cue in required_cues
        )

        if is_preferred:
            preferred_skills.update(skills)
        elif is_required:
            required_skills.update(skills)

    preferred_skills -= required_skills

    return sorted(required_skills), sorted(preferred_skills)


def get_skill_context(text, skill, window=180):
    normalized = normalize_text(text)
    pattern = get_skill_pattern(skill)
    contexts = []

    try:
        matches = list(
            re.finditer(pattern, normalized, re.IGNORECASE)
        )
    except re.error:
        return contexts

    for match in matches:
        start = max(0, match.start() - window)
        end = min(len(normalized), match.end() + window)
        contexts.append(normalized[start:end])

    return contexts


def contains_phrase(text, phrase):
    text = normalize_text(text)
    phrase = normalize_text(phrase)

    if not phrase:
        return False

    return bool(
        re.search(
            r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
            text
        )
    )


def count_context_evidence(contexts, words):
    return sum(
        1
        for context in contexts
        if any(contains_phrase(context, word) for word in words)
    )


def extract_years_of_experience(text, skill):
    contexts = get_skill_context(text, skill, 220)
    values = []

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s+years?",
        r"(\d+(?:\.\d+)?)\+?\s+yrs?"
    ]

    for context in contexts:
        for pattern in patterns:
            for value in re.findall(pattern, context):
                try:
                    years = float(value)
                    if 0 <= years <= 60:
                        values.append(years)
                except ValueError:
                    continue

    return max(values) if values else 0.0


def detect_proficiency(resume_text, skill):
    contexts = get_skill_context(resume_text, skill, 220)

    if not contexts:
        return "Not Found"

    strong = count_context_evidence(contexts, STRONG_WORDS)
    practical = count_context_evidence(contexts, PRACTICAL_WORDS)
    intermediate = count_context_evidence(
        contexts, INTERMEDIATE_WORDS
    )
    familiar = count_context_evidence(contexts, FAMILIAR_WORDS)

    project_words = [
        "project", "projects", "implemented in",
        "developed using", "built using", "final year project",
        "academic project", "personal project"
    ]

    project_evidence = count_context_evidence(
        contexts, project_words
    )

    years = extract_years_of_experience(resume_text, skill)

    if familiar and not practical and not project_evidence:
        return "Familiar"

    if strong and (practical or project_evidence or years >= 2):
        return "Advanced"

    if years >= 3 and (practical or project_evidence):
        return "Advanced"

    if practical or project_evidence or intermediate or years >= 1:
        return "Intermediate"

    if strong:
        return "Advanced"

    return "Mentioned"


def get_proficiency_score(proficiency):
    scores = {
        "Expert": 1.00,
        "Advanced": 0.90,
        "Intermediate": 0.75,
        "Familiar": 0.50,
        "Mentioned": 0.30,
        "Not Found": 0.00
    }

    return scores.get(proficiency, 0.0)


def get_skill_proficiency_details(resume_text, skill):
    contexts = get_skill_context(resume_text, skill, 220)
    proficiency = detect_proficiency(resume_text, skill)

    return {
        "skill": skill,
        "proficiency": proficiency,
        "score": get_proficiency_score(proficiency),
        "mentions": len(contexts),
        "years": extract_years_of_experience(resume_text, skill)
    }


def get_all_skill_proficiency(resume_text, skills):
    return {
        skill: get_skill_proficiency_details(resume_text, skill)
        for skill in skills
    }
