# import sys
# import json


# def execute_function(code, args):
#     exec_globals = {}
#     try:
#         exec(code, exec_globals)
#         if "main" in exec_globals:
#             result = exec_globals["main"](*args)
#             return {"result": result}
#         else:
#             return {"error": "No 'main' function defined."}
#     except Exception as e:
#         return {"error": str(e)}


# if __name__ == "__main__":
#     try:
#         input_data = json.loads(sys.argv[1])
#         code = input_data.get("code")
#         args = input_data.get("args", [])
#         output = execute_function(code, args)
#         print(json.dumps(output))
#     except json.JSONDecodeError:
#         print(json.dumps({"error": "Invalid JSON input"}))
import sys
import json
import io
import contextlib
import builtins

def execute_function(code, args):
    exec_globals = {}
    logs = []
    errors = []
    result = None

    # Capture stdout and stderr
    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            # Allow safe built-ins and some basic imports (e.g., math, random, etc.)
            safe_builtins = {
                'print': print,
                'range': range,
                'len': len,
                'int': int,
                'float': float,
                'str': str,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'abs': abs,
                'sum': sum,
                '__builtins__': {}
            }

            # Inject only safe modules
            allowed_imports = {"math", "random", "time", "datetime"}

            # Monkey-patch __import__ to block unsafe modules
            def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                if name in allowed_imports:
                    return __import__(name, globals, locals, fromlist, level)
                raise ImportError(f"Import of module '{name}' is not allowed.")

            safe_builtins['__import__'] = safe_import

            exec(code, {"__builtins__": safe_builtins}, exec_globals)

            if "main" in exec_globals:
                result = exec_globals["main"](*args)
            else:
                errors.append("No 'main' function defined.")
    except Exception as e:
        errors.append(str(e))

    logs_output = stdout.getvalue().splitlines()
    error_output = stderr.getvalue().splitlines()
    logs.extend(logs_output)
    errors.extend(error_output)

    response = {
        "logs": logs,
        "errors": errors,
    }

    if result is not None:
        response["result"] = result

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
