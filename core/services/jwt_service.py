from typing import Type

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.tokens import BlacklistMixin, Token

from core.enums.action_token_enum import ActionTokenEnum
from core.exceptions.jwt_exception import JWTException

UserModel = get_user_model()
ActionTokenClassType = Type[BlacklistMixin | Token]


class ActionToken(BlacklistMixin, Token):
    pass


class ActivateToken(ActionToken):
    token_type = ActionTokenEnum.ACTIVATE.token_type
    lifetime = ActionTokenEnum.ACTIVATE.lifetime


class RecoveryToken(ActionToken):
    token_type = ActionTokenEnum.RECOVERY.token_type
    lifetime = ActionTokenEnum.RECOVERY.lifetime


class JWTService:
    @staticmethod
    def create_token(user, token_class: ActionTokenClassType):
        return token_class.for_user(user)

    @staticmethod
    def validate_token(token, token_class: ActionTokenClassType):
        try:
            token_res = token_class(token)
            token_res.check_blacklist()
        except Exception as e:
            print(f"JWT Validation Error: {e}")
            raise JWTException

        token_res.blacklist()
        user_id = token_res.payload.get('user_id')

        print(f"Decoded user_id from token: {user_id}")

        return get_object_or_404(UserModel, pk=user_id)

