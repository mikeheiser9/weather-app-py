"""Typed aliases for the async MongoDB driver.

Motor's classes are generic over the stored document type. These aliases pin
that to ``dict[str, Any]`` so strict typing is satisfied without repeating the
parameter at every call site.
"""

from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MongoDatabase = AsyncIOMotorDatabase[dict[str, Any]]
MongoClient = AsyncIOMotorClient[dict[str, Any]]
