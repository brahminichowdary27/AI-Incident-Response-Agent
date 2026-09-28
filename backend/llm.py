import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=GEMINI_API_KEY)

PRIMARY_MODEL = "gemini-3.1-flash-lite"
FALLBACK_MODEL = "gemini-3.6-flash"


def generate_response(prompt):

    models = [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model in models:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                return response.text

            except Exception as e:

                last_error = e

                print(
                    f"Gemini error using {model}, "
                    f"attempt {attempt + 1}/3: {repr(e)}"
                )

                if attempt < 2:

                    wait_time = 3 * (2 ** attempt)

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

        print(
            f"Primary attempts exhausted for {model}. "
            "Trying next model..."
        )

    raise RuntimeError(
        f"Gemini generation failed after retries: {last_error}"
    )