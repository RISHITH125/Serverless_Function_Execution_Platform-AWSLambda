import sys
import json
import io
import contextlib
import builtins
import traceback

SAFE_MODULES = {"datetime", "math", "random", "time"}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in SAFE_MODULES:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import of module '{name}' is not allowed")


def main_wrap(code:str) ->str:
    indented_code = "\n".join([f"    {line}" for line in code.splitlines()])
    return f"def main(*args):\n{indented_code}"

def execute_function(code, args):
    exec_globals = {}
    logs = []
    errors = []
    result = None

    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    safe_globals = {
        "__builtins__": builtins.__dict__.copy(),
    }
    safe_globals["__builtins__"]["__import__"] = safe_import


    try:
        if "def main" not in code:
            code = main_wrap(code)

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            exec(code, safe_globals)
            if "main" in safe_globals:
                result = safe_globals["main"](*args)
            else:
                errors.append("No 'main' function defined.")
    except Exception:
        errors.append(traceback.format_exc())

    logs += stdout_capture.getvalue().splitlines()
    errors += stderr_capture.getvalue().splitlines()

    response ={
        "logs": logs,
        "errors": errors,
        "result": result
    }

    return response

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.argv[1])
        code = input_data.get("code")
        args = input_data.get("args", [])
        output = execute_function(code, args)
        print(json.dumps(output))
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input", "logs": [], "errors": ["Invalid JSON"]}))
