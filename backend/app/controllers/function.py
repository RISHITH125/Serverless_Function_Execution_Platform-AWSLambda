from app.core import jwt
from fastapi import APIRouter, Header, HTTPException, status
from app.models.function import Function
from app.core.jwt import decode_jwt_token
from app.database.mongodb import db

router = APIRouter()


@router.post("/function")
async def store_function(function: Function, authorization: str = Header(...)):
    split_token = authorization.split(" ")
    if len(split_token) != 2:  # Bearer token
        raise HTTPException(400, "Invalid token format")
    try:
        username = decode_jwt_token(split_token[1])["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    if not await db["users"].find_one({"username": username}):
        raise HTTPException(404, "User not found")

    existing = await db["functions"].find_one(
        {
            "username": username,
            "$or": [{"name": function.name}, {"route": function.route}],
        }
    )
    if existing:
        raise HTTPException(409, "Function with same name or route exists")

    function_dict = function.dict()
    function_dict["username"] = username
    function_dict["language"] = function.language.value
    await db["functions"].insert_one(function_dict)
    return {"message": "Function stored successfully"}
