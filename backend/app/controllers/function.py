from app.core.security import validate_user
from fastapi import APIRouter, Header, HTTPException
from app.models.function import Function
from app.database.mongodb import db

router = APIRouter()


@router.post("/function")
async def store_function(function: Function, authorization: str = Header(...)):
    username = await validate_user(authorization)

    function_dict = function.dict()
    function_dict["username"] = username
    function_dict["language"] = function.language.value
    try:
        await db["functions"].insert_one(function_dict)
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(409, f"Function with same name or route exists")
        raise HTTPException(500, f"Error storing function")
    return {"message": "Function stored successfully"}


@router.get("/function/{function_name}")
async def get_function(function_name: str, authorization: str = Header(...)):
    username = await validate_user(authorization)

    function = await db["functions"].find_one(
        {"username": username, "name": function_name}
    )
    if not function:
        raise HTTPException(404, "Function not found")
    function.pop("_id", None)
    function.pop("username", None)
    return function


@router.delete("/function/{function_name}")
async def delete_function(function_name: str, authorization: str = Header(...)):
    username = await validate_user(authorization)

    await db["functions"].delete_one({"username": username, "name": function_name})
    return {"message": "Function deleted successfully"}


@router.put("/function/{function_name}")
async def update_function(
    function_name: str, function: Function, authorization: str = Header(...)
):
    username = await validate_user(authorization)

    function_to_update = await db["functions"].find_one(
        {
            "username": username,
            "name": function_name,
        }
    )

    if not function_to_update:
        raise HTTPException(404, "Function not found")

    await db["functions"].update_one(
        {"_id": function_to_update["_id"]},
        {
            "$set": {
                "name": function.name,
                "route": function.route,
                "language": function.language.value,
                "code": function.code,
                "timeout": function.timeout,
            }
        },
    )

    return {"message": "Function updated successfully"}
