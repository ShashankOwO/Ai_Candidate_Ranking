from pydantic import BaseModel


class QualificationCreate(BaseModel):

    university: str
    degree: str
    specialization: str | None = None
    percentage: float | None = None
    passed_out_year: int | None = None
    joining_year: int | None = None