from fastapi import APIRouter, HTTPException, status
from app.models.user import User
from app.database.mongodb import db
from app.core.security import hash_password, check_passwords_match
from app.core.jwt import create_jwt_token

router = APIRouter()


@router.post("/signup")
async def signup(user: User):
    user.password = hash_password(user.password)
    if await db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=409, detail="User already exists")
    await db["users"].insert_one(user.dict())
    token = create_jwt_token({"sub": user.username})
    return {"access_token": token}


@router.post("/login")
async def login(user: User):
    existing = await db["users"].find_one({"username": user.username})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    if not check_passwords_match(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token({"sub": user.username})
    return {"access_token": token}
