import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from schemas.candidate_extraction import CandidateExtraction

load_dotenv()

key = os.getenv("GROQ_API_KEY")

print("API key loaded:", key is not None)
print("API key length:", len(key) if key else 0)

llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)



structured_llm=llm.with_structured_output(CandidateExtraction,method="function_calling",)


def extract_candidate_data(resume_text:str)->CandidateExtraction:
    prompt=f"""

You are an AI resume information extraction system.

Extract information ONLY from the resume text provided below.

Do not invent information.

If information is missing, return null.

Extract:

1. Candidate personal details
2. Skills
3. Professional experience
4. Qualifications
5. Projects

For skills:
- Identify the skill name
- Category
- Proficiency if explicitly available
- Years of experience if explicitly available

For experience:
- Company
- Job title
- Start date
- End date
- Years
- Description

For qualifications:
- University
- Degree
- Specialization
- Percentage
- Passed out year
- Joining year if available

For projects:
- Project name
- Description
- Technologies
- Role
- Duration

Resume text:

{resume_text}

    """

    result=structured_llm.invoke(prompt)
    return result