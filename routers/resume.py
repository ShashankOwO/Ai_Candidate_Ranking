import os
import uuid

from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from sqlalchemy.orm import Session
from database import getdb
from models.candidate import Candidate
from models.resume import Resume

router=APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR="uploads/resumes"

ALLOWED_TYPES={
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}




@router.post("/resume")
async def upload_resume(candidate_id:int,file:UploadFile=File(...),db:Session=Depends(getdb)):

    candidate=db.query(Candidate).filter(Candidate.candidate_id==candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF/DOC/DOCX files are allowed"
        )

    os.makedirs(UPLOAD_DIR,exist_ok=True)

    extension=os.path.splitext(file.filename)[1]

    unique_name=f"{uuid.uuid4()}{extension}"

    file_path=os.path.join(UPLOAD_DIR,unique_name)

    file_content=await file.read()

    with open(file_path,"wb") as output_file:
        output_file.write(file_content)

    resume=Resume(
        candidate_id=candidate_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(file_content)
    )


    db.add(resume)
    db.commit()
    db.refresh(resume)

    return{
        "message":"Resume Uploaded Successfully",
        "resume_id":resume.resume_id,
        "candidate_id":candidate_id,
        "filename":resume.file_name
    }



    









