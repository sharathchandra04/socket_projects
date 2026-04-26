class Message:

    def __init__(self, version, msg_type, payload):
        self.version = version
        self.msg_type = msg_type
        self.payload = payload

    def __repr__(self):
        return f"<Message type={self.msg_type} len={len(self.payload)}>"