import os
import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def evaluate_ai_criteria(
    job_description: str,
    candidate_information: str,
    criteria: list
):

    criteria_text = ""

    for criterion in criteria:

        criteria_text += f"""
Criterion ID: {criterion.criteria_id}
Criterion Name: {criterion.criteria_name}
Criterion Type: {criterion.criteria_type}
Description: {criterion.criteria_description}
"""

    prompt = f"""
You are an AI candidate evaluation system.

JOB DESCRIPTION:
{job_description}

CANDIDATE INFORMATION:
{candidate_information}

EVALUATION CRITERIA:
{criteria_text}

Evaluate each criterion.

Rules:

- Score every criterion from 0 to 100.
- Use only the candidate information.
- Do not invent information.
- Give a short reason.
- Return JSON only.

Format:

{{
    "results": [
        {{
            "criteria_id": 1,
            "score": 85,
            "reason": "Short explanation"
        }}
    ]
}}
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):

        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    try:

        result = json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "AI returned invalid JSON"
            )

        result = json.loads(
            content[start:end + 1]
        )

    return result["results"]