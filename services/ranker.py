import pandas as pd


def normalize_inverse(series: pd.Series) -> pd.Series:
    """
    Lower-is-better normalization.
    Example: latency, cost.
    Converts values to a 0-1 range where lower original values score higher.
    """
    if series.nunique() == 1:
        return pd.Series([1.0] * len(series), index=series.index)

    min_value = series.min()
    max_value = series.max()

    return 1 - ((series - min_value) / (max_value - min_value))


def normalize_direct(series: pd.Series) -> pd.Series:
    """
    Higher-is-better normalization.
    Example: quality.
    Converts values to a 0-1 range.
    """
    if series.nunique() == 1:
        return pd.Series([1.0] * len(series), index=series.index)

    min_value = series.min()
    max_value = series.max()

    return (series - min_value) / (max_value - min_value)


def add_overall_score(
    df: pd.DataFrame,
    quality_weight: float = 0.5,
    latency_weight: float = 0.3,
    cost_weight: float = 0.2,
) -> pd.DataFrame:
    """
    Adds normalized component scores and a weighted overall score.
    """
    ranked_df = df.copy()

    ranked_df["quality_component"] = normalize_direct(ranked_df["quality_score"])
    ranked_df["latency_component"] = normalize_inverse(ranked_df["latency_seconds"])
    ranked_df["cost_component"] = normalize_inverse(ranked_df["estimated_cost_usd"])

    ranked_df["overall_score"] = (
        ranked_df["quality_component"] * quality_weight
        + ranked_df["latency_component"] * latency_weight
        + ranked_df["cost_component"] * cost_weight
    ).round(4)

    ranked_df["normalized_quality"] = ranked_df["quality_component"]
    ranked_df["normalized_latency"] = ranked_df["latency_component"]
    ranked_df["normalized_cost"] = ranked_df["cost_component"]

    return ranked_df.sort_values("overall_score", ascending=False).reset_index(drop=True)
