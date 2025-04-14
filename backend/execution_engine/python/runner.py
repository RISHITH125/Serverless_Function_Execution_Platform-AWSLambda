import sys
import json


def execute_function(code, args):
    exec_globals = {}
    try:
        exec(code, exec_globals)
        if "main" in exec_globals:
            result = exec_globals["main"](*args)
            return {"result": result}
        else:
            return {"error": "No 'main' function defined."}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        input_data = json.loads(sys.argv[1])
        code = input_data.get("code")
        args = input_data.get("args", [])
        output = execute_function(code, args)
        print(json.dumps(output))
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
