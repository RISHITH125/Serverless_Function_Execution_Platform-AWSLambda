import time
from fastapi import APIRouter, HTTPException, Request
import asyncio
from app.database.mongodb import db
from execution_engine.core.container_utils import exec_function

router = APIRouter()


@router.post("/{username}/execute/{function_name}/{route:path}")
async def run_function(username: str, function_name: str, route: str, request: Request):

    try:
        body = await request.json()
        args = body.get("args", [])
    except Exception as e:
        args = []

    function = await db["functions"].find_one(
        {
            "username": username,
            "name": function_name,
            "route": f"/{route}",
        }
    )

    if not function:
        raise HTTPException(404, "Function not found")

    language = function["language"]
    code = function["code"]
    timeout = function["timeout"]
    function_name = function["name"]
    PoolManager = request.app.state.pool
    if not PoolManager:
        raise HTTPException(503, "No available pool manager")
    print(f"[+] Timeout for function {function_name}: {timeout} seconds")
    container = await PoolManager.get_available_container(language)
    if not container:
        raise HTTPException(503, "No available containers")
    try:
        print(
            f"[+] Running function {function_name} in container {container.name} with args {args}"
        )
        start_time = time.monotonic()
        result = await asyncio.wait_for(
            asyncio.to_thread(exec_function, container, code, args, language),
            timeout=timeout / 1000,
        )
    except asyncio.TimeoutError:
        print(
            f"[!] Execution of function {function_name} timed out in container {container.name}"
        )

        async def stop_container():
            await PoolManager.forceStopContainer(container)

        await stop_container()
        raise HTTPException(408, "Function execution timed out")
    except Exception as e:
        print(f"Error executing function {function_name}: {str(e)}")
        raise HTTPException(500, f"Error executing function: {str(e)}")
    finally:
        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        
        await PoolManager.release_container(container)
        # Add the elapsed time to the result
        if isinstance(result, dict):
            result["execution_time_seconds"] = round(elapsed_time, 4)
        else:
            result = {
                "result": result,
                "execution_time_seconds": round(elapsed_time, 4)
            }
    return result
