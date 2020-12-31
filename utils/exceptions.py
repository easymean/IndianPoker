import logging

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

logger = logging.getLogger('exception')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    if response.status_code/100 == 4:
        logger.warning(exc.detail)
    else:
        logger.error(exc.detail)

    return response


class GameDidNotStart(APIException):
    status_code = 405
    default_detail = '게임이 시작되지 않았습니다.'
    default_code = 'service unavailable'


class GameAlreadyStarted(APIException):
    status_code = 405
    default_detail = '게임이 이미 시작상태입니다.'
    default_code = 'service unavailable'


class RoomAlreadyFull(APIException):
    status_code = 405
    default_detail = '방이 가득 찼습니다.'
    default_code = 'service unavailable'


class InvalidSocket(APIException):
    status_code = 400
    default_detail = 'socket closed unexpectedly'
    default_code = 'socket error'


class UserDoesNotExist(APIException):
    status_code = 404
    default_detail = "유저가 존재하지 않습니다."
    default_code = "user not found"


class ParsingException(APIException):
    status_code = 404
    default_detail = 'None 타입은 파싱이 불가합니다.'
    default_code = 'parse error'
