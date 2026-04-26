import random
import json


class ClientGenerator:
    def generate(self):
        # Simple protocol message (custom binary/text hybrid)
        req_type = random.choice(["PING", "ECHO", "SUM"])

        if req_type == "PING":
            payload = {"type": "PING", "data": ""}

        elif req_type == "ECHO":
            payload = {"type": "ECHO", "data": "hello"}

        else:
            payload = {
                "type": "SUM",
                "data": [random.randint(1, 100) for _ in range(5)]
            }

        # newline delimited protocol (simple framing)
        return (json.dumps(payload) + "\n").encode()