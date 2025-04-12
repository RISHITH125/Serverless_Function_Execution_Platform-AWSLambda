from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["lambda_project"]


async def create_indexes():
    await db["users"].create_index("username", unique=True)
    await db["functions"].create_index([("username", 1), ("name", 1)], unique=True)
    await db["functions"].create_index([("username", 1), ("route", 1)], unique=True)
