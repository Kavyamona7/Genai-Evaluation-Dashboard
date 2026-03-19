import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    return OpenAI(api_key=api_key)


def call_model(model: str, prompt: str, temperature: float) -> tuple[str, float]:
    """
    Calls the selected OpenAI model and returns:
    - output text
    - latency in seconds
    """
    client = get_openai_client()

    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Respond clearly, accurately, and in a structured way."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    latency = round(time.time() - start_time, 2)
    output_text = response.choices[0].message.content.strip()

    return output_text, latency
