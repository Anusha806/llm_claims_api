# parser.py
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def parse_query_with_gemini(query: str):
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    prompt = f"""
You are an intelligent insurance assistant.
Given a natural language query, extract the following fields as JSON. Do not include any explanation or extra text — just valid JSON:

- age (integer)
- gender (male/female/unknown)
- procedure (string)
- location (string)
- policy_duration_months (integer)

Query:
"{query}"
"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.strip("`").replace("json", "").strip()
        return json.loads(response_text)
    except Exception as e:
        return {
            "error": "Failed to parse Gemini response",
            "raw_response": response.text if 'response' in locals() else str(e)
        }
