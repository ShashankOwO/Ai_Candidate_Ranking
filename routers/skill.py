from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.skill import Skill
from models.user import User
from schemas.skill import SkillCreate, SkillResponse
from utils.auth import get_current_user


router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


@router.post(
    "/",
    response_model=SkillResponse
)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    existing_skill = (
        db.query(Skill)
        .filter(
            Skill.skill_name == skill_data.skill_name
        )
        .first()
    )

    if existing_skill:
        raise HTTPException(
            status_code=400,
            detail="Skill already exists"
        )

    skill = Skill(
        skill_name=skill_data.skill_name,
        skill_category=skill_data.skill_category
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill