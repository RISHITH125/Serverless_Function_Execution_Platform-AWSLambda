import asyncio
import time
# from .container_utils import start_container, stop_container, is_container_alive
import dotenv
import os
# from runtime_factory import get_runtime
from .runtime_factory import get_runtime

dotenv.load_dotenv(".env.local")
LANGUAGE_CONFIG = {
    "python": {
        "dockerfile_path": os.path.join(os.path.dirname(__file__), "../python"),
        "image": "python-function-runner",
        "exec_cmd": ["python", "runner.py"],
    },
    "javascript": {
        "dockerfile_path": os.path.join(os.path.dirname(__file__), "../javascript"),
        "image": "javascript-function-runner",
        "exec_cmd": ["node", "runner.js"],
    },
}

runtime_type = os.getenv("RUNTIME", "DOCKER").lower()
use_gvisor = os.getenv("RUNTIME", "").lower() == "gvisor"


runtime = get_runtime(runtime_type, LANGUAGE_CONFIG, use_gvisor)
class WarmPoolManager:
    def __init__(self, config):
        self.pools = {}
        self.lock = asyncio.Lock()
        self.config = config

    @classmethod
    async def create(cls, config):
        self = cls(config)
        await self._initialize_pools()
        return self

    async def _initialize_pools(self):
        for language, conf in self.config.items():
            if language not in self.pools:
                self.pools[language] = []
                for _ in range(conf["initial"]):
                    # container = await asyncio.to_thread(start_container, language)
                    container = await asyncio.to_thread(runtime.start_container, language)
                    self.pools[language].append({"container": container, "busy": False})
                print(f"[+] Initialized container for {language}")

    async def get_available_container(self, language):
        async with self.lock:
            pool = self.pools.get(language, [])

            if not pool:
                self.pools[language] = []
                for _ in range(self.config[language]["initial"]):
                    # container = await asyncio.to_thread(start_container, language)
                    container = await asyncio.to_thread(runtime.start_container, language)
                    self.pools[language].append({"container": container, "busy": False})
                pool = self.pools[language]
            for entry in pool:
                # if not entry["busy"] and is_container_alive(entry["container"]):
                if not entry["busy"] and runtime.is_container_alive(entry["container"]):
                    print(f"[+] Found available container {entry['container'].id} for {language}")
                    entry["busy"] = True
                    return entry["container"]

            # If no available container, create a new one if within limit
            if len(pool) < self.config[language]["max"]:
                # container = await asyncio.to_thread(start_container, language)
                container = await asyncio.to_thread(runtime.start_container, language)
                self.pools[language].append({"container": container, "busy": True})
                return container
            else:
                print(
                    f"[!] No available container for {language} and max limit reached"
                )
                return None

    async def release_container(self, container):
        async with self.lock:
            for pool in self.pools.values():
                for entry in pool:
                    if entry["container"].id == container.id:
                        entry["busy"] = False
                        print(f"[+] Released container {container.id}")
                        return

    async def scale_down_idle(self, timeout=60):
        """
        Peridically run this in a background thread to scale down idle containers
        """

        while True:
            async with self.lock:
                for language, pool in self.pools.items():
                    initialize_size = self.config[language]["initial"]
                    for entry in pool:
                        if len(pool) <= initialize_size:
                            break
                        # if not entry["busy"] and is_container_alive(entry["container"]):
                        if not entry["busy"] and runtime.is_container_alive(entry["container"]):
                            print(
                                f"[-] Scaling down container {entry['container'].id} for {language}"
                            )
                            await asyncio.to_thread(
                                # stop_container, entry["container"].id
                                runtime.stop_container, entry["container"]
                            )
                            pool.remove(entry)

            await asyncio.sleep(timeout)

    async def shutdown(self):
        async with self.lock:
            for language, pool in self.pools.items():
                for entry in pool:
                    # if is_container_alive(entry["container"]):
                    if runtime.is_container_alive(entry["container"]):
                        # await asyncio.to_thread(stop_container, entry["container"].id)
                        await asyncio.to_thread(runtime.stop_container, entry["container"])
                        
                self.pools[language] = []
        print("[-] Shutdown all containers and cleared pools")
        return True

    async def forceStopContainer(self, container):
        async with self.lock:
            for pool in self.pools.values():
                for entry in pool:
                    if entry["container"].id == container.id:
                        # await asyncio.to_thread(stop_container, container.id)
                        await asyncio.to_thread(runtime.stop_container, container)
                        entry["busy"] = False
                        pool.remove(entry)
                        print(f"[-] Force stopped container {container.id}")
                        return True

        return True
    async def exec_function(self, container, code, args, language):
        return await asyncio.to_thread(runtime.exec_function, container, code, args, language)
