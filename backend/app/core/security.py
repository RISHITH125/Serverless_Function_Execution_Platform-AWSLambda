from fastapi import HTTPException
import bcrypt

from app.core.jwt import decode_jwt_token
from app.core import jwt
from app.database.mongodb import db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_passwords_match(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def validate_user(authorization: str):
    split_token = authorization.split(" ")
    if len(split_token) != 2:
        raise HTTPException(400, "Invalid token format")
    try:
        username = decode_jwt_token(split_token[1])["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not await db["users"].find_one({"username": username}):
        raise HTTPException(404, "User not found")
    return username
