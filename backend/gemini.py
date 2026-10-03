import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_gemini_analysis(analysis, risk):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "message": "Gemini API key not found"}

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an AI cybersecurity analyst.

Analyze the following STATIC security analysis of a file.
The file has NOT been executed.

Important rules:
1. Do not claim a file is definitely malware unless there is strong evidence.
2. Distinguish between: Clean, Suspicious, Potentially malicious, Confirmed malicious, and Security test file.
3. If EICAR is detected, clearly explain that EICAR is a harmless standard antivirus testing signature and NOT actual malware.
4. Distinguish between rule-based findings and actual threats.
5. Base your assessment only on the supplied static-analysis evidence.

FILE ANALYSIS:
{analysis}

RULE-BASED RISK RESULT:
{risk}

Return the response using exactly these sections:
SUMMARY:
RISK ASSESSMENT:
SUSPICIOUS INDICATORS:
RECOMMENDED ACTIONS:
"""

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
        )

        return {
            "success": True,
            "model": MODEL_NAME,
            "report": interaction.output_text,
        }

    except Exception as error:
        return {"success": False, "message": str(error)}