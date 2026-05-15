from __future__ import annotations

from fastapi import APIRouter, Depends

from ..database import db
from ..deps import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/summary")
async def summary(_: dict = Depends(require_roles("admin"))) -> dict:
    total_users = await db.users.count_documents({})
    total_courses = await db.courses.count_documents({})
    published_courses = await db.courses.count_documents({"status": "published"})
    total_orders = await db.orders.count_documents({})
    paid_orders = await db.orders.count_documents({"status": "paid"})
    total_enrollments = await db.enrollments.count_documents({})
    return {
        "users": total_users,
        "courses": total_courses,
        "published_courses": published_courses,
        "orders": total_orders,
        "paid_orders": paid_orders,
        "enrollments": total_enrollments,
    }
