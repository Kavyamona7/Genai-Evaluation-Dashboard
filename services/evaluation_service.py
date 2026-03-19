from services.model_runner import call_model
from services.metrics import estimate_cost, count_response_words


def run_single_evaluation(model: str, prompt: str, temperature: float) -> dict:
    """
    Runs one model evaluation and returns a structured result row.
    """
    output_text, latency = call_model(
        model=model,
        prompt=prompt,
        temperature=temperature
    )

    response_length_words = count_response_words(output_text)
    estimated_cost = estimate_cost(model, prompt, output_text)

    return {
        "model": model,
        "prompt": prompt,
        "response": output_text,
        "latency_seconds": latency,
        "response_length_words": response_length_words,
        "estimated_cost_usd": estimated_cost,
        "quality_score": 3,
        "relevance_score": 3,
        "clarity_score": 3,
        "completeness_score": 3,
    }
