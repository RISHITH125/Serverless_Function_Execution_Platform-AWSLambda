import requests
import time
import random

# I'm tryna put you in the worst mood, ah
# P1 cleaner than your church shoes, ah ....

def get_random_number():
    return random.randint(1, 1000)

while True:
    try:
        function_url = "http://localhost:8000/rahul/execute/add/comedy"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "args": [get_random_number(), get_random_number()]
        }

        response = requests.post(function_url, headers=headers, json=data)
        print(response.json())
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

    # no waiting, because why not :)
    # let it be chaotic 🚀

    # time.sleep(0.25)
