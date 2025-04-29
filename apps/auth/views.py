from django.contrib.auth import get_user_model
from django.db import IntegrityError

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from core.dataclasses.user_dataclass import UserDataClass
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

        try:
            user = UserModel.objects.create(
                email=data["email"],
                username=data["username"],
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

        EmailService.register(user)

        return Response({"detail": "Activation email sent."}, status=status.HTTP_200_OK)


class RecoveryPasswordRequestView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = EmailSerializer

    def post(self, *args, **kwargs):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(UserModel, **serializer.data)
        EmailService.recovery_password(user)
        return Response({'detail': 'check your email'}, status=status.HTTP_200_OK)


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
