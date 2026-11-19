def calculate_final_score(
    technical_score,
    microsoft_score,
    education_score,
    project_score,
    similarity_score
):

    overall_score = (
    technical_score * 0.35
    + microsoft_score * 0.25
    + education_score * 0.15
    + project_score * 0.10
    + similarity_score * 0.15
)

    return round(
        overall_score,
        2
    )


def get_recommendation(score):

    if score >= 80:
        return "Strong Match"

    elif score >= 65:
        return "Good Match"

    elif score >= 50:
        return "Moderate Match"
    
    elif score >= 40:
        return "Low Match"

    else:
        return "Very Low Match"