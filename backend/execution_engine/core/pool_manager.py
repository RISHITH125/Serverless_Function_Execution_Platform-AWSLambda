import asyncio
import time
from .container_utils import start_container, stop_container, is_container_alive

class WarmPoolManager:
    def __init__(self,config):
        self.pools = {}
        self.lock = asyncio.Lock()
        self.config = config

    @classmethod
    async def create(cls, config):
        self = cls(config)
        await self._initialize_pools()
        return self

    async def _initialize_pools(self):
        for language , conf in self.config.items():
            self.pools[language] = []
            for _ in range(conf["initial"]):
                container = await asyncio.to_thread(start_container, language)
                self.pools[language].append({'container': container, 'busy': False})
            print(f"[+] Initialized container for {language}")
        
    async def get_available_container(self, language):
        async with self.lock:
            pool = self.pools.get(language,[])
            for entry in pool:
                if not entry['busy'] and is_container_alive(entry['container']):
                    entry['busy'] = True
                    return entry['container']

            # If no available container, create a new one if within limit
            if len(pool) < self.config[language]["max"]:
                container = await asyncio.to_thread(start_container, language)
                self.pools[language].append({"container": container, 'busy': True})
                return container
            else:
                print(f"[!] No available container for {language} and max limit reached")
                return None
    
    async def release_container(self, container):
        async with self.lock:
            for entry in self.pools.values():
                for entry in entry:
                    if entry['container'].id == container.id:
                        entry['busy'] = False
                        print(f"[+] Released container {container.id}")
                        return

    async def scale_down_idle(self,timeout=60):
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
                        if not entry['busy'] and is_container_alive(entry['container']):
                            print(f"[-] Scaling down container {entry['container'].id} for {language}")
                            await asyncio.to_thread(stop_container, entry['container'].id)
                            pool.remove(entry)
            time.sleep(timeout)


    async def shutdown(self):
        async with self.lock:
            for language, pool in self.pools.items():
                for entry in pool:
                    if is_container_alive(entry['container']):
                        await asyncio.to_thread(stop_container, entry['container'].id)
                self.pools[language] = []
        print("[-] Shutdown all containers and cleared pools")
        return True