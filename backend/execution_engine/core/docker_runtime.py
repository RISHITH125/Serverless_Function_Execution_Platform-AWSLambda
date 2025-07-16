import docker
import uuid
import json
import os 

from .container_runtime import ContainerRuntime



class DockerContainerRuntime(ContainerRuntime):
    def __init__(self, config, use_gvisor):
        self.config = config
        self.use_gvisor = use_gvisor
        self.client = docker.from_env()

    def get_language_config(self, language):
        config= self.config.get(language)
        if config is None:
            raise ValueError(f"Unsupported language: {language}")
        return config

    def build_image(self, language):
        config = self.get_language_config(language)       
        image_name = config["image"]
        image_path = config["dockerfile_path"]
        if not os.path.isdir(image_path):
            raise RuntimeError(f"Dockerfile path '{image_path}' does not exist or is not a directory.")
        
        images = self.client.images.list(name=image_name)
        if not images:
            print(f"[!] Image '{image_name}' not found. Building it...")
            try:
                image, logs = self.client.images.build(path=image_path, tag=image_name)
                for chunk in logs:
                    if "stream" in chunk:
                        print(chunk["stream"].strip())
                print(f"[+] Successfully built image '{image_name}'")
            except Exception as e:
                raise RuntimeError(f"Failed to build image '{image_name}': {e}")
        else:
            print(f"[+] Image '{image_name}' already exists.")

    def start_container(self, language):
        # Ensure the image exists before starting the container
        self.build_image(language)
        config = self.get_language_config(language)
        
        container_name = f"{language}_runner_{uuid.uuid4().hex[:8]}"

        host_config = self.client.api.create_host_config(runtime="runsc") if self.use_gvisor else None

        container = self.client.api.create_container(
            image=config["image"],
            command=["sleep", "infinity"],
            name=container_name,
            stdin_open=True,
            detach=True,
            tty=True,
            host_config=host_config
            )
        self.client.api.start(container=container.get("Id"))
        print(f"[+] Started container '{container_name}' for language '{language}' with {'gvisor' if self.use_gvisor else 'default runtime'}")
        return self.client.containers.get(container.get("Id"))
    
    def stop_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            print(f"[-] Stopped and removed container '{container_id}'")
        except docker.errors.NotFound:
            print(f"[!] Container '{container_id}' not found")
        except Exception as e:
            print(f"[!] Error stopping container '{container_id}': {e}")
    
    def exec_function(self, container, code, args, language):
        try:
            input_data = {"code": code, "args": args}
            input_json = json.dumps(input_data)
            config= self.get_language_config(language)
            cmd = config["exec_cmd"] + [input_json]
            exec_result = container.exec_run(
                cmd,
                stdout=True,
                stdin=True,
                stderr=True,
                tty=True,
                demux=True
            )

            stdout, stderr = exec_result.output
            if stderr:
                return {"error": stderr.decode("utf-8").strip()}
            try:
                return json.loads(stdout.decode("utf-8").strip())
            except json.JSONDecodeError:
                return {"error": "Failed to decode JSON output from execution","raw": stdout.decode()}
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}
        
    def is_container_alive(self, container):
        try:
            container.reload()  # Refresh the container state
            return container.status == "running"
        except docker.errors.NotFound:
            return False
        except Exception as e:
            print(f"[!] Error checking container status: {e}")
            return False