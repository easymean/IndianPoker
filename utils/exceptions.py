from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class InvalidMethod(APIException):
    status_code = 400
    default_detail = "Invalid method"
    default_code = "invalid_method"


class SocketError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


class UserDoesNotExist(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = "User Does Not Exist"
