from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from core.dataclasses.user_dataclass import UserDataClass
from core.exceptions.create_manager_exceptions import UsernameTooLongException
from core.services.email_service import EmailService
from core.services.jwt_service import ActivateToken, JWTService, RecoveryToken

from apps.auth.serializers import EmailSerializer, PasswordSerializer
from apps.users.models import ProfileModel
from apps.users.models import UserModel as User
from apps.users.serializers import UserSerializer

UserModel = get_user_model()


class CreateManagerView(CreateAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data.get("username", "")
        max_length = UserModel._meta.get_field("username").max_length

        email = data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"detail": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        if len(username) > max_length:
            raise UsernameTooLongException(max_length)

        try:
            user = UserModel.objects.create(
                email=email,
                username=username,
                is_manager=False,
                is_active=False
            )

            profile_data = data.get("profile")
            if profile_data:
                ProfileModel.objects.create(
                    first_name=profile_data.get("first_name", ""),
                    last_name=profile_data.get("last_name", ""),
                    user=user
                )

            return Response({"detail": "User created. Admin must activate the account."}, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                return Response({"detail": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "Database integrity error."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSetPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordSerializer

    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        user = JWTService.validate_token(token, ActivateToken)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.data["password"])
        user.is_active = True
        user.is_manager = True
        user.save()

        return Response({'detail': 'Account activated and password set.'}, status=status.HTTP_200_OK)


class UserActivateView(GenericAPIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        user = get_object_or_404(UserModel, id=user_id, is_active=False)

        activation_link = EmailService.register(user)

        return Response({
            "detail": "Activation email sent.",
            "activation_link": activation_link
        }, status=status.HTTP_200_OK)


class RecoveryPasswordRequestView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = EmailSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(UserModel, **serializer.data)
        recovery_link = EmailService.recovery_password(user)
        return Response({'detail': 'check your email',  "recovery_link": recovery_link}, status=status.HTTP_200_OK)


class RecoveryPasswordView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        token = kwargs['token']
        user: User = JWTService.validate_token(token, RecoveryToken)
        user.set_password(serializer.data['password'])
        user.save()
        return Response({'detail': 'password was changed'}, status=status.HTTP_200_OK)
