from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

client = AsyncIOMotorClient(settings.mongo_url)
db: AsyncIOMotorDatabase = client[settings.mongo_db]


async def init_indexes() -> None:
    await db.users.create_index("email", unique=True)
    await db.courses.create_index("slug", unique=True)
    await db.orders.create_index("user_id")
    await db.orders.create_index("course_id")
    await db.enrollments.create_index([("user_id", 1), ("course_id", 1)], unique=True)
