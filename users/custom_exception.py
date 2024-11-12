from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    status_code = 403
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail, code=None):
        self.detail = {'response': detail}
        if code is not None:
            self.status_code = code