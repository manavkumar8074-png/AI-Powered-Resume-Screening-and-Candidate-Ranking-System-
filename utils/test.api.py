
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

try:
    print("Checking available models...")

    for model in client.models.list():
        print(model.name)

    print("\nTesting Gemini response...")

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say Hello"
    )

    print("Gemini Response:", response.text)

except Exception as error:
    print("API ERROR:", error)
