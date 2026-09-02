import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import getdb
from models.candidate import Candidate
from models.resume import Resume
from models.user import User
from schemas.resume import ResumeResponse
from services.candidate_extractor import extract_candidate_data
from services.candidate_persistence import save_candidate_data
from services.resume_parser import extract_resume_text
from utils.auth import get_current_user

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

UPLOAD_DIR = "uploads/resumes"

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF/DOC/DOCX files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(file.filename or "")[1]
    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    file_content = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(file_content)

    try:
        raw_text = extract_resume_text(
            file_path, file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract resume text: {str(e)}"
        )

    candidate_data = extract_candidate_data(raw_text)

    try:
        candidate = save_candidate_data(
            extracted_data=candidate_data,
            user_id=current_user.user_id,
            db=db
        )
    except Exception:
        db.rollback()
        raise

    resume = Resume(
        candidate_id=candidate.candidate_id,
        file_name=file.filename or "resume",
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(file_content),
        raw_text=raw_text,
        uploaded_at=datetime.now(timezone.utc)
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume Uploaded Successfully",
        "resume_id": resume.resume_id,
        "candidate_id": candidate.candidate_id,
        "candidate_name": candidate.full_name,
        "filename": resume.file_name,
        "file_size": resume.file_size,
        "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
        "text_length": len(raw_text)
    }


@router.get("/all", response_model=list[ResumeResponse])
@router.get("", response_model=list[ResumeResponse])
def get_all_resumes(
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.candidate_id)
        .filter(Candidate.user_id == current_user.user_id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )

    resume_list = []
    for resume, candidate in results:
        resume_list.append(
            ResumeResponse(
                resume_id=resume.resume_id,
                candidate_id=resume.candidate_id,
                candidate_name=candidate.full_name,
                candidate_email=candidate.email_address,
                file_name=resume.file_name,
                file_type=resume.file_type,
                file_size=resume.file_size,
                uploaded_at=resume.uploaded_at,
                raw_text=resume.raw_text,
            )
        )
    return resume_list


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume_by_id(
    resume_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.candidate_id)
        .filter(Resume.resume_id == resume_id, Candidate.user_id == current_user.user_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume, candidate = result
    return ResumeResponse(
        resume_id=resume.resume_id,
        candidate_id=resume.candidate_id,
        candidate_name=candidate.full_name,
        candidate_email=candidate.email_address,
        file_name=resume.file_name,
        file_type=resume.file_type,
        file_size=resume.file_size,
        uploaded_at=resume.uploaded_at,
        raw_text=resume.raw_text,
    )


@router.get("/{resume_id}/download")
def download_resume_file(
    resume_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.candidate_id)
        .filter(Resume.resume_id == resume_id, Candidate.user_id == current_user.user_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume, _ = result
    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server")

    return FileResponse(
        path=resume.file_path,
        media_type=resume.file_type,
        filename=resume.file_name
    )


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    result = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.candidate_id)
        .filter(Resume.resume_id == resume_id, Candidate.user_id == current_user.user_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume, _ = result
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except OSError:
            pass

    db.delete(resume)
    db.commit()

    return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id
    }
