from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..database import db
from ..deps import get_current_user, require_roles
from ..mappers import course_public
from ..schemas import CourseCreateRequest, CourseResponse, CourseUpdateRequest

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    status_filter: str | None = Query(default="published", alias="status"),
) -> list[CourseResponse]:
    query = {}
    if status_filter:
        query["status"] = status_filter
    docs = await db.courses.find(query).sort("created_at", -1).to_list(length=500)
    return [course_public(doc) for doc in docs]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str) -> CourseResponse:
    doc = await db.courses.find_one({"_id": course_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course_public(doc)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreateRequest,
    user: dict = Depends(require_roles("admin", "creator")),
) -> CourseResponse:
    existing_slug = await db.courses.find_one({"slug": payload.slug})
    if existing_slug:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")

    doc = {
        "_id": str(uuid4()),
        "title": payload.title,
        "slug": payload.slug,
        "description": payload.description,
        "price_inr": payload.price_inr,
        "status": payload.status,
        "creator_id": user["_id"],
        "module_slugs": payload.module_slugs,
        "video_locales": payload.video_locales,
        "created_at": datetime.now(timezone.utc),
    }
    await db.courses.insert_one(doc)
    return course_public(doc)


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    payload: CourseUpdateRequest,
    user: dict = Depends(get_current_user),
) -> CourseResponse:
    doc = await db.courses.find_one({"_id": course_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if user["role"] not in {"admin"} and doc["creator_id"] != user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await db.courses.update_one({"_id": course_id}, {"$set": updates})
        doc.update(updates)
    return course_public(doc)
