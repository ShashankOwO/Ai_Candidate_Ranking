from pydantic import BaseModel

class SkillExtraction(BaseModel):
    skill_name:str
    skill_category:str|None=None
    proficiency:str|None=None
    years_experience:str|None=None


class ExperienceExtraction(BaseModel):
    company_name:str
    job_title:str|None=None
    start_date:str|None=None
    end_date:str|None=None
    years:int|None=None
    description:str|None=None

class QualificationExtraction(BaseModel):
    university:str|None=None
    degree:str|None=None
    specialization:str|None=None
    percentage:float|None=None
    passed_out_year:int|None=None
    joining_year:int|None=None

class ProjectExtraction(BaseModel):
    project_name:str
    description:str|None=None
    technologies:str|None=None
    role:str|None=None
    duration:str|None=None

class CandidateExtraction(BaseModel):
    full_name:str
    contact_no:str|None=None
    email_address:str|None=None

    skills:list[SkillExtraction]=[]
    experiences:list[ExperienceExtraction]=[]
    qualifications:list[QualificationExtraction]=[]
    projects:list[ProjectExtraction]=[]
