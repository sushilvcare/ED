from __future__ import annotations

from .schemas import CourseResponse, EnrollmentResponse, OrderResponse, UserPublic


def user_public(doc: dict) -> UserPublic:
    return UserPublic(
        id=doc["_id"],
        email=doc["email"],
        full_name=doc["full_name"],
        role=doc["role"],
        created_at=doc["created_at"],
    )


def course_public(doc: dict) -> CourseResponse:
    return CourseResponse(
        id=doc["_id"],
        title=doc["title"],
        slug=doc["slug"],
        description=doc["description"],
        price_inr=doc["price_inr"],
        status=doc["status"],
        creator_id=doc["creator_id"],
        module_slugs=doc.get("module_slugs", []),
        video_locales=doc.get("video_locales", {}),
        created_at=doc["created_at"],
    )


def order_public(doc: dict) -> OrderResponse:
    return OrderResponse(
        id=doc["_id"],
        user_id=doc["user_id"],
        course_id=doc["course_id"],
        amount_inr=doc["amount_inr"],
        status=doc["status"],
        payment_provider=doc["payment_provider"],
        payment_ref=doc.get("payment_ref"),
        created_at=doc["created_at"],
    )


def enrollment_public(doc: dict) -> EnrollmentResponse:
    return EnrollmentResponse(
        id=doc["_id"],
        user_id=doc["user_id"],
        course_id=doc["course_id"],
        order_id=doc["order_id"],
        created_at=doc["created_at"],
    )
