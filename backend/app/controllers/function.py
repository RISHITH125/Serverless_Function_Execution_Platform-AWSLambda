from app.core.security import validate_user
from fastapi import APIRouter, Header, HTTPException ,Request
from app.models.function import Function
from app.database.mongodb import db
from app.core.config import DOMAIN

router = APIRouter()

domain = DOMAIN or "http://localhost:8000"  


@router.post("/function")
async def store_function(function: Function,  request: Request, authorization: str = Header(...)):
    username = await validate_user(authorization)

    function_dict = function.dict()
    function_dict["username"] = username
    function_dict["language"] = function.language.value

    PoolManager=request.app.state.pool
    if not PoolManager:
        raise HTTPException(503, "No available pool manager")
    try:
        await db["functions"].insert_one(function_dict)
        await PoolManager._initialize_pools()

    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(409, f"Function with same name or route exists")
        raise HTTPException(500, f"Error storing function")
    
    route_url = f"{domain}/{username}/execute/{function.name}{function.route}" 
    return {"message": "Function stored successfully","execution_url":route_url}


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


@router.get("/functions")
async def get_functions(authorization: str = Header(...)):
    username = await validate_user(authorization)

    functions = await db["functions"].find({"username": username}).to_list(length=None)
    for function in functions:
        function.pop("_id", None)
        function.pop("username", None)
    return functions
