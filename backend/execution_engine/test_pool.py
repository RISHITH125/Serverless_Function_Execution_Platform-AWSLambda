import asyncio
from concurrent.futures import ThreadPoolExecutor
from core.pool_manager import WarmPoolManager
from core.container_utils import exec_function


# PYTHON sample function
# sample_code = """
# def main(a, b):
#     import time
#     now = time.time()
#     while time.time() - now < 2:  # simulate 2s block
#         pass
#     return a + b
# """

# JAVASCRIPT sample function
sample_code = """
function main(a, b) {
    const now = Date.now();
    while (Date.now() - now < 2000); // simulate 2s block
    return a + b;
}
"""

# This will run the blocking function in a thread
async def run_exec_in_thread(pool, args, loop, executor):
    container = await pool.get_available_container("javascript")
    if container is None:
        print("No available container for execution")
        return None

    try:
        print(f"Executing function in container {container.name} with args: {args}")
        result = await loop.run_in_executor(executor, exec_function, container, sample_code, args, "javascript")
        print(f"Execution result: {result}")
    finally:
        await pool.release_container(container)

async def main():
    # pool config
    config = {
        "javascript": {
            "initial": 2,
            "max": 5,
        }
    }
    pool = WarmPoolManager(config)
    await pool._initialize_pools()

    # setup thread pool executor
    executor = ThreadPoolExecutor(max_workers=5)
    loop = asyncio.get_event_loop()

    # First batch of requests (run in parallel threads)
    await asyncio.gather(
        run_exec_in_thread(pool, (), loop, executor),
        run_exec_in_thread(pool, (1,2), loop, executor),
        run_exec_in_thread(pool, (), loop, executor),
    )

    await asyncio.sleep(5)  # just spacing things out for clarity

    # Second batch
    await asyncio.gather(
        run_exec_in_thread(pool, (7, 8), loop, executor),
        run_exec_in_thread(pool, (9, 10), loop, executor),
    )

    # cleanup
    await pool.shutdown()
    executor.shutdown(wait=True)
    print("Pool shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
