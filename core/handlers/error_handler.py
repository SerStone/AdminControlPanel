from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from core.exceptions.create_manager_exceptions import UsernameTooLongException
from core.exceptions.invavid_enum_exceptions import InvalidEnumValueError
from core.exceptions.user_status_exceptions import UserAlreadyActiveException, UserAlreadyBlockedException


def error_handler(exc: Exception, context: dict) -> Response:
    handlers = {
        'JWTException': _jwt_validation_error,
        'InvalidEnumValueError': _invalid_enum_value_error,
        'UserAlreadyBlockedException': _user_already_blocked_error,
        'UserAlreadyActiveException': _user_already_active_error,
        'UsernameTooLongException': _username_too_long_error,
    }

    response = exception_handler(exc, context)
    exc_class = exc.__class__.__name__

    if exc_class in handlers:
        return handlers[exc_class](exc, context)

    return response


def _jwt_validation_error(exc: Exception, context: dict) -> Response:
    return Response({'detail': 'JWT token is invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)


def _invalid_enum_value_error(exc: InvalidEnumValueError, context: dict) -> Response:
    return Response(exc._generate_message(), status=status.HTTP_400_BAD_REQUEST)


def _user_already_blocked_error(exc: Exception, context: dict) -> Response:
    return Response({'detail': 'User is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)


def _user_already_active_error(exc: Exception, context: dict) -> Response:
    return Response({'detail': 'User is already active.'}, status=status.HTTP_400_BAD_REQUEST)


def _username_too_long_error(exc: UsernameTooLongException, context: dict) -> Response:
    return Response(
        {"detail": f"Username is too long. Maximum length is {exc.max_length} characters."},
        status=status.HTTP_400_BAD_REQUEST
    )