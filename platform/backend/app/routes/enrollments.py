from __future__ import annotations

from fastapi import APIRouter, Depends

from ..database import db
from ..deps import get_current_user
from ..mappers import enrollment_public
from ..schemas import EnrollmentResponse

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/my", response_model=list[EnrollmentResponse])
async def my_enrollments(user: dict = Depends(get_current_user)) -> list[EnrollmentResponse]:
    docs = await db.enrollments.find({"user_id": user["_id"]}).sort("created_at", -1).to_list(length=500)
    return [enrollment_public(doc) for doc in docs]
