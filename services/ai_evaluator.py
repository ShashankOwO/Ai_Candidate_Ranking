import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-120b",temperature=0,api_key=os.getenv("GROQ_API_KEY"))

def evaluate_candidate_criterion(candidate_data:str,criterion_name:str,criterion_description:str):
    prompt=f"""
You are evaluating a candidate for a recruitment system.

Evaluation criterion:
{criterion_name}

Criterion description:
{criterion_description}

Candidate information:
{candidate_data}

Give a score between 0 and 100.

Only use information present in the candidate information.

Do not invent facts.

Return:

Score: <number>
Reason: <short explanation>
"""
    response=llm.invoke(prompt)

    return response.content