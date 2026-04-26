def handle_request(request):
    """
    request: parsed object from your protocol
    return: response object (to be serialized)
    """

    # Example protocol fields assumed:
    # request.type, request.data

    if request.type == "PING":
        return {"type": "PONG", "data": b""}

    elif request.type == "ECHO":
        return {"type": "ECHO_RESPONSE", "data": request.data}

    elif request.type == "SUM":
        nums = request.data  # assume list[int]
        return {"type": "SUM_RESPONSE", "data": sum(nums)}

    else:
        return {"type": "ERROR", "data": b"UNKNOWN"}