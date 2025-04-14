import asyncio
from core.pool_manager import WarmPoolManager
from core.container_utils import exec_function

# PYTHON
# sample_code="""
# def main(x,y):
#     return x+y
# """

# JAVASCRIPT
sample_code="""
function main(x,y){
    return x+y;
}
""" 



async def test_execution(pool,args):
    container =await pool.get_available_container("javascript")
    # container2=await pool.get_available_container("javascript")
    # if container:
    #     result = await exec_function(container, sample_code, args)
    #     print(f"Execution result: {result}")
    #     pool.release_container(container)
    # else:
    #     print("No available container for execution")
    if container is None:
        print("No available container for execution")
        return None
    try:
        print(f"Executing function in container {container.name} with args: {args}")
        result = exec_function(container, sample_code, args,"javascript")
        print(f"Execution result: {result}")
    finally:
        await pool.release_container(container)

    
async def main():
    # create a pool with 2 python containers
    config = {
        "javascript": {
            "initial": 2,
            "max": 5,
        }
    }
    pool = WarmPoolManager(config)
    await pool._initialize_pools()

    # simulating multiple requests
    await asyncio.gather(
        test_execution(pool, (1, 2)),
        test_execution(pool, (3, 4)),
        test_execution(pool, (5, 6)),
    )

    await asyncio.sleep(5)  # wait for a while to see the output

    await asyncio.gather(
        test_execution(pool, (7, 8)),
        test_execution(pool, (9, 10)),
    )

    # clenaup
    await pool.shutdown()
    print("Pool shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())