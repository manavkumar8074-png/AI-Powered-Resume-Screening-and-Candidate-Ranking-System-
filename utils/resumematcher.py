import re
import math
from collections import Counter

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "from", "by",
    "with", "as", "this", "that", "these", "those",
    "it", "its", "you", "your", "our", "they", "their",
    "will", "can", "could", "should", "would", "have",
    "has", "had", "do", "does", "did", "using", "used"
}


def tokenize(text):
    text = str(text or "").lower()
    text = text.replace("object-oriented", "object oriented")
    text = text.replace("problem-solving", "problem solving")

    words = re.findall(r"\b[a-z0-9_+#.]+\b", text)

    return [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]


def create_features(words):
    features = list(words)

    for index in range(len(words) - 1):
        features.append(
            words[index] + " " + words[index + 1]
        )

    return Counter(features)


def calculate_similarity(resume_text, job_description):
    resume_features = create_features(tokenize(resume_text))
    job_features = create_features(tokenize(job_description))

    if not resume_features or not job_features:
        return 0.0

    documents = [
        set(resume_features),
        set(job_features)
    ]

    document_frequency = Counter()

    for document in documents:
        document_frequency.update(document)

    total_documents = len(documents)
    vocabulary = set(resume_features) | set(job_features)

    idf = {
        term: math.log(
            (1 + total_documents) /
            (1 + document_frequency[term])
        ) + 1
        for term in vocabulary
    }

    resume_vector = {
        term: count * idf[term]
        for term, count in resume_features.items()
    }

    job_vector = {
        term: count * idf[term]
        for term, count in job_features.items()
    }

    common_terms = set(resume_vector) & set(job_vector)

    dot_product = sum(
        resume_vector[term] * job_vector[term]
        for term in common_terms
    )

    resume_magnitude = math.sqrt(
        sum(value ** 2 for value in resume_vector.values())
    )

    job_magnitude = math.sqrt(
        sum(value ** 2 for value in job_vector.values())
    )

    if resume_magnitude == 0 or job_magnitude == 0:
        return 0.0

    similarity = dot_product / (
        resume_magnitude * job_magnitude
    )

    return round(max(0.0, min(similarity * 100, 100.0)), 2)
