import os
import uuid

from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from sqlalchemy.orm import Session
from database import getdb
from models.candidate import Candidate

router=APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)




