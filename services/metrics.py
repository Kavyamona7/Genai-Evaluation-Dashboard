def estimate_cost(model: str, input_text: str, output_text: str) -> float:
    """
    Rough cost estimation based on total word count.
    This is not exact billing.
    """
    input_words = len(input_text.split())
    output_words = len(output_text.split())
    total_words = input_words + output_words

    pricing = {
        "gpt-4o-mini": 0.00002,
        "gpt-4.1-mini": 0.00003,
    }

    rate = pricing.get(model, 0.000025)
    return round(total_words * rate, 4)


def count_response_words(text: str) -> int:
    return len(text.split())
