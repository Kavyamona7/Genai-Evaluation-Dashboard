import pandas as pd


def get_recommendations(df: pd.DataFrame) -> dict:
    """
    Returns the best models by key business criteria.
    """
    if df.empty:
        return {
            "fastest": None,
            "cheapest": None,
            "best_quality": None,
            "best_overall": None,
        }

    return {
        "fastest": df.loc[df["latency_seconds"].idxmin(), "model"],
        "cheapest": df.loc[df["estimated_cost_usd"].idxmin(), "model"],
        "best_quality": df.loc[df["quality_score"].idxmax(), "model"],
        "best_overall": df.loc[df["overall_score"].idxmax(), "model"]
        if "overall_score" in df.columns
        else None,
    }
