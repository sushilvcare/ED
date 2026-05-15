from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Role = Literal["admin", "creator", "student"]
CourseStatus = Literal["draft", "published", "archived"]
OrderStatus = Literal["pending", "paid", "failed", "refunded"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)
    role: Role = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime


class CourseCreateRequest(BaseModel):
    title: str
    slug: str
    description: str
    price_inr: int = Field(ge=0)
    status: CourseStatus = "draft"
    module_slugs: list[str] = []
    video_locales: dict[str, str] = {}


class CourseUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price_inr: int | None = Field(default=None, ge=0)
    status: CourseStatus | None = None
    module_slugs: list[str] | None = None
    video_locales: dict[str, str] | None = None


class CourseResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    price_inr: int
    status: CourseStatus
    creator_id: str
    module_slugs: list[str]
    video_locales: dict[str, str]
    created_at: datetime


class OrderCreateRequest(BaseModel):
    course_id: str


class OrderResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    amount_inr: int
    status: OrderStatus
    payment_provider: str
    payment_ref: str | None = None
    created_at: datetime


class MarkOrderPaidRequest(BaseModel):
    payment_provider: Literal["manual", "stripe", "razorpay"] = "manual"
    payment_ref: str | None = None


class EnrollmentResponse(BaseModel):
    id: str
    user_id: str
    course_id: str
    order_id: str
    created_at: datetime
