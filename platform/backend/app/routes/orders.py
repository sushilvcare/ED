from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import db
from ..deps import get_current_user, require_roles
from ..mappers import order_public
from ..schemas import MarkOrderPaidRequest, OrderCreateRequest, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreateRequest, user: dict = Depends(get_current_user)) -> OrderResponse:
    course = await db.courses.find_one({"_id": payload.course_id, "status": "published"})
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Published course not found")

    doc = {
        "_id": str(uuid4()),
        "user_id": user["_id"],
        "course_id": payload.course_id,
        "amount_inr": course["price_inr"],
        "status": "pending",
        "payment_provider": "manual",
        "payment_ref": None,
        "created_at": datetime.now(timezone.utc),
    }
    await db.orders.insert_one(doc)
    return order_public(doc)


@router.post("/{order_id}/mark-paid", response_model=OrderResponse)
async def mark_order_paid(
    order_id: str,
    payload: MarkOrderPaidRequest,
    user: dict = Depends(require_roles("admin")),
) -> OrderResponse:
    _ = user  # role check only
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    await db.orders.update_one(
        {"_id": order_id},
        {
            "$set": {
                "status": "paid",
                "payment_provider": payload.payment_provider,
                "payment_ref": payload.payment_ref,
            }
        },
    )
    order.update(
        {
            "status": "paid",
            "payment_provider": payload.payment_provider,
            "payment_ref": payload.payment_ref,
        }
    )

    existing = await db.enrollments.find_one({"user_id": order["user_id"], "course_id": order["course_id"]})
    if not existing:
        await db.enrollments.insert_one(
            {
                "_id": str(uuid4()),
                "user_id": order["user_id"],
                "course_id": order["course_id"],
                "order_id": order_id,
                "created_at": datetime.now(timezone.utc),
            }
        )
    return order_public(order)


@router.get("/my", response_model=list[OrderResponse])
async def my_orders(user: dict = Depends(get_current_user)) -> list[OrderResponse]:
    docs = await db.orders.find({"user_id": user["_id"]}).sort("created_at", -1).to_list(length=500)
    return [order_public(doc) for doc in docs]
