class GeneralException(Exception):
    pass

class RoutingException(GeneralException):
    status_code = 400

    def __init__(self, message):
        self.message = {'error': message}

class RequestException(GeneralException):
    status_code = 400

    def __init__(self, message):
        self.message = {'error': message}

class DatabaseQueryException(GeneralException):
    status_code = 400

    def __init__(self, message):
        self.message = {'error': message}