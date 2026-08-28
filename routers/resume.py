import os
import uuid

from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from sqlalchemy.orm import Session
from database import getdb
from models.candidate import Candidate
from models.resume import Resume
from services.resume_parser import extract_resume_text
from services.candidate_extractor import extract_candidate_data
from services.candidate_extractor import extract_candidate_data
from services.candidate_persistence import save_candidate_data
from utils.auth import get_current_user
from models.user import User

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




@router.post("/upload")
async def upload_resume(file:UploadFile=File(...),db:Session=Depends(getdb),current_user:User=Depends(get_current_user)):

    

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


    try:

        raw_text=extract_resume_text(
            file_path,file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract resume text:{str(e)}"
        )

    candidate_data=extract_candidate_data(raw_text)

    try:
        candidate = save_candidate_data(
            extracted_data=candidate_data,
            user_id=current_user.user_id,
            db=db
        )
    except Exception:
        db.rollback()
        raise

    

    resume=Resume(
        candidate_id=candidate.candidate_id,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(file_content),
        raw_text=raw_text
    )


    db.add(resume)
    db.commit()
    db.refresh(resume)

    return{
        "message":"Resume Uploaded Successfully",
        "resume_id":resume.resume_id,
        "candidate_id":candidate.candidate_id,
        "filename":resume.file_name,
        "text_length":len(raw_text)
    }



    









