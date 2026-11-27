class APIServerException(Exception):
    pass


class APIBadRequest(Exception):
    pass


class APIForbidden(Exception):
    pass


class APIUnauthorized(Exception):
    pass


class APINotFound(Exception):
    pass
