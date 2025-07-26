import os
import re
import json
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pypdf import PdfReader
from dotenv import load_dotenv
import openai

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LLM Claims API is up and running!"}


def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_entities(query: str) -> dict:
    age = re.search(r"(\d{1,3})[- ]?year[- ]?old", query.lower())
    procedure = re.search(r"(knee surgery|heart surgery|bypass|replacement|treatment)", query.lower())
    location = re.search(r"in ([a-zA-Z\s]+?)(?:,|\.|\s|$)", query.lower())
    duration = re.search(r"(\d+)[ -]?(month|year)", query.lower())

    return {
        "age": int(age.group(1)) if age else None,
        "procedure": procedure.group(1) if procedure else "",
        "location": location.group(1).strip() if location else "",
        "policy_duration": duration.group(0) if duration else "",
    }


def query_gpt(policy_text: str, query_text: str):
    prompt = f"""
You are an insurance claim evaluator. Based on the policy document below and a claim query, determine:

1. Whether the claim is APPROVED or REJECTED.
2. If approved, how much amount is claimable?
3. What clause or content matched the query?
4. If rejected, why?

Policy Document:
\"\"\"
{policy_text}
\"\"\"

Query:
\"\"\"
{query_text}
\"\"\"

Respond in JSON with fields: decision, justification, amount, matched_clause, similarity_score (0 to 1 scale).
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "decision": "rejected",
            "justification": f"GPT Error: {str(e)}",
            "amount": "₹0",
            "matched_clause": "",
            "similarity_score": 0.0
        }


@app.post("/evaluate")
async def evaluate(query: str = Form(...), file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    parsed = extract_entities(query)
    result = query_gpt(text, query)
    result["parsed_query"] = parsed
    return JSONResponse(content=result)
