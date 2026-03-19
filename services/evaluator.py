from typing import Dict


def calculate_quality_score(
    relevance_score: int,
    clarity_score: int,
    completeness_score: int,
) -> float:
    """
    Compute the average manual quality score.
    """
    return round(
        (relevance_score + clarity_score + completeness_score) / 3,
        2,
    )


def update_result_quality_scores(result: Dict) -> Dict:
    """
    Return the result dict with refreshed quality_score.
    """
    relevance = int(result.get("relevance_score", 3))
    clarity = int(result.get("clarity_score", 3))
    completeness = int(result.get("completeness_score", 3))

    result["quality_score"] = calculate_quality_score(
        relevance_score=relevance,
        clarity_score=clarity,
        completeness_score=completeness,
    )
    return result
