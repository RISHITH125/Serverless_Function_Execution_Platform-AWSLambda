import docker
import uuid
import json
import os


client = docker.from_env()

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
    }
}

def build_image(language):
    config = LANGUAGE_CONFIG.get(language)
    if config is None:
        raise ValueError(f"Unsupported language: {language}")

    image_name = config["image"]
    image_path = config["dockerfile_path"]
    if not os.path.isdir(image_path):
        raise RuntimeError(f"Dockerfile path '{image_path}' does not exist or is not a directory.")

    images = client.images.list(name=image_name)
    if not images:
        print(f"[!] Image '{image_name}' not found. Building it...")
        try:
            image, logs = client.images.build(
                path=image_path,
                tag=image_name
            )
            for chunk in logs:
                if 'stream' in chunk:
                    print(chunk['stream'].strip())
            print(f"[+] Successfully built image '{image_name}'")
        except Exception as e:
            raise RuntimeError(f"Failed to build image '{image_name}': {e}")
    else:
        print(f"[+] Image '{image_name}' already exists.")


def start_container(language):
    # Ensure the image exists before starting the container
    build_image(language)

    config = LANGUAGE_CONFIG.get(language)
    if config is None:
        raise ValueError(f"Unsupported language: {language}")
    
    container_name = f"{language}_runner_{uuid.uuid4().hex[:8]}"
    
    container = client.containers.run(
        image=config["image"],
        command=['sleep', 'infinity'],
        name=container_name,
        stdin_open=True,
        stdout=True,
        stderr=True,
        detach=True,
        tty=True,
    )

    print(f"[+] Started container {container_name} for {language}")
    return container

def stop_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        print(f"[-] Stopped and removed container: {container_id}")
    except docker.errors.NotFound:
        print(f"[!] Container {container_id} not found for stop request")

def exec_function(container, code, args, language):
    try:
        input_data = {
            "code": code,
            "args": args
        }

        input_json = json.dumps(input_data)
        config = LANGUAGE_CONFIG.get(language)
        if config is None:
            return {"error": f"Unsupported language: {container.image.tags[0].split(':')[0]}"}
        
        cmd= config["exec_cmd"] + [input_json]

        exec_result = container.exec_run(
            cmd,
            stdin=True,
            stdout=True,
            stderr=True,
            tty=False,
            demux=True,
        )
        stdout, stderr = exec_result.output

        if stderr:
            return {"error": stderr.decode("utf-8").strip()}
        try:
            return json.loads(stdout.decode("utf-8").strip())
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON output","raw":stdout.decode()}
    except Exception as e:
        return {"error": str(e)}
    

def is_container_alive(container):
    try:
        container.reload()
        return container.status == 'running'
    except docker.errors.NotFound:
        return False
