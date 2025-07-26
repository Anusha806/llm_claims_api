# main.py
import os
import json
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from utils.loader import extract_text_from_pdf
from utils.evaluator import evaluate
from utils.parser import parse_query_with_gemini

import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("Loaded Gemini API Key:", os.getenv("GEMINI_API_KEY"))
app = FastAPI()

# Ensure data directory exists
os.makedirs("data/documents", exist_ok=True)

@app.get("/")
def root():
    return {"message": "LLM Claims API is up and running!"}

@app.post("/evaluate")
async def evaluate_query(query: str = Form(...), file: UploadFile = File(...)):
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = f"data/documents/{file_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Extract and parse
        policy_text = extract_text_from_pdf(file_path)

        parsed_query = await parse_query_with_gemini(query) \
            if callable(getattr(parse_query_with_gemini, "__await__", None)) else parse_query_with_gemini(query)
        
        gemini_response = await query_gemini(policy_text, query)

        rule_decision = evaluate(parsed_query, gemini_response.get("matched_clause", ""))

        final_result = {
            **gemini_response,
            "parsed_query": parsed_query,
            "rule_based_decision": rule_decision,
        }

    except Exception as e:
        final_result = {
            "error": str(e)
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return JSONResponse(content=final_result)


async def query_gemini(policy_text: str, query_text: str):
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    
    prompt = f"""
You are an insurance claim evaluator. Based on the policy document and query, respond in JSON with:
1. decision: 'approved' or 'rejected'
2. justification: brief explanation
3. amount: estimated payout
4. matched_clause: snippet of the policy that supports the decision
5. similarity_score: float between 0 and 1

Policy:
{policy_text}

Query:
{query_text}
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        # Clean markdown-style code formatting
        if content.startswith("```json") or content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        return {
            "decision": "rejected",
            "justification": f"Gemini Error: {str(e)}",
            "amount": "₹0",
            "matched_clause": "",
            "similarity_score": 0.0
        }
