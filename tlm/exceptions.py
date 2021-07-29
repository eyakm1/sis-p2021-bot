class BaseResponseException(Exception):
    status_code = 500


class Http403(BaseResponseException):
    status_code = 403


class Http409(BaseResponseException):
    status_code = 409
