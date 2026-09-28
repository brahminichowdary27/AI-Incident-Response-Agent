import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.8-flash"

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_response(prompt):

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text