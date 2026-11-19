import re


def preprocess_text(text):
    text = text.lower()

    # Normalize common variations
    text = text.replace(
        "scikit-learn",
        "scikit learn"
    )

    text = text.replace(
        "object-oriented programming",
        "object oriented programming"
    )

    text = text.replace(
        "restful api",
        "rest api"
    )

    # Keep letters, numbers and spaces
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text