from .docker_runtime import DockerContainerRuntime

def get_runtime(runtime_type,config,use_gvisor=False):
    """
    Factory function to get the appropriate runtime instance based on the runtime type.
    """
    if runtime_type == "docker":
        return DockerContainerRuntime(config, use_gvisor)
    elif runtime_type == "containerd":
        print("[!] containerd runtime is not implemented yet")
        return None
    else:
        raise ValueError(f"Unsupported runtime type: {runtime_type}")