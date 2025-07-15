import time
from fastapi import APIRouter, HTTPException, Request
import asyncio
from app.database.mongodb import db
from execution_engine.core.container_utils import exec_function
import requests

router = APIRouter()

metrics_service_url = "http://localhost:8080/update/metrics"

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

        # asyncio.create_task(stop_container(PoolManager, container))


        raise HTTPException(408, "Function execution timed out")
    except Exception as e:
        print(f"Error executing function {function_name}: {str(e)}")
        raise HTTPException(500, f"Error executing function: {str(e)}")
    finally:
        

            # Only measure time if no timeout occurred
            end_time = time.monotonic()
            elapsed_time = end_time - start_time
        
            routeInfo = f"{username}_{function_name}"
            headers = {"Content-Type": "application/json"}
            data = {
                "route": routeInfo,
                "executiontime": elapsed_time
            }
        
            # Attempt to send metrics (but ignore errors)
            try:
                response = requests.post(
                    metrics_service_url,
                    headers=headers,
                    json=data,
                    timeout=2  # don't wait forever
                )
                if response.status_code == 204:
                    print(f"[✓] Metrics sent for {routeInfo} - execution time: {elapsed_time:.4f}s")
                else:
                    print(f"[!] Metrics server responded with status {response.status_code}")
            except requests.RequestException as e:
                print(f"[!] Could not send metrics: {str(e)}")
        
            # Release container no matter what
            await PoolManager.release_container(container)
        
            try:
                if isinstance(result, dict):
                    result["execution_time_seconds"] = round(elapsed_time, 4)
                else:
                    raise HTTPException(500, f"Result is not a dict: {str(result)}")
            except Exception as e:
                print(f"[!] Failed to attach execution time: {str(e)}")
                raise HTTPException(500, "Internal error while processing result.")
        


    return result



async def stop_container(PoolManager, container):
    await PoolManager.forceStopContainer(container)
    print(f"Stopped container {container.name} due to timeout.")