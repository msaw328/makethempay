# given a request and a dict of param name -> type pairs
# it checkes whether the request is json and all params
# are present nad have proper types
def is_json_request_valid(request, params):
    if not request.is_json:
        return False

    for param in params:
        if not param in request.json or not isinstance(request.json[param], params[param]):
            return False

    return True


