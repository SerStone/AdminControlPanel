from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.enums import StatusEnum
from core.exceptions.user_status_exceptions import UserAlreadyActiveException, UserAlreadyBlockedException
from core.permissions.is_admin_or_write_only_permissions import IsAdminOrWriteOnlyPermission
from core.permissions.is_superuser import IsSuperuser

from apps.users.serializers import UserSerializer

from .models import UserModel as User

UserModel = get_user_model()


class UserCreateView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()
    permission_classes = (IsAdminOrWriteOnlyPermission,)

    def get_queryset(self):
        return UserModel.objects.annotate(
            total_orders=Count('managed_orders'),
            orders_new=Count('managed_orders', filter=Q(managed_orders__status=StatusEnum.New.value)),
            orders_in_work=Count('managed_orders', filter=Q(managed_orders__status=StatusEnum.InWork.value)),
            orders_agree=Count('managed_orders', filter=Q(managed_orders__status=StatusEnum.Aggre.value)),
            orders_disagree=Count('managed_orders', filter=Q(managed_orders__status=StatusEnum.Disaggre.value)),
            orders_dubbing=Count('managed_orders', filter=Q(managed_orders__status=StatusEnum.Dubbing.value))
        ).order_by('-id')


class MeView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


class UserToAdminView(GenericAPIView):
    permission_classes = (IsSuperuser,)

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id)

    def put(self, *args, **kwargs):
        user: User = self.get_object()

        if not user.is_staff:
            user.is_staff = True
            user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


class AdminToUserView(GenericAPIView):
    permission_classes = (IsSuperuser,)

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id)

    def put(self, *args, **kwargs):
        user: User = self.get_object()

        if user.is_staff:
            user.is_staff = False
            user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


class UserBlockView(GenericAPIView):
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id)

    def put(self, *args, **kwargs):
        user: User = self.get_object()

        if not user.is_active:
            raise UserAlreadyBlockedException()

        user.is_active = False
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUnBlockView(GenericAPIView):
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return UserModel.objects.exclude(id=self.request.user.id)

    def put(self, *args, **kwargs):
        user: User = self.get_object()

        if user.is_active:
            raise UserAlreadyActiveException()

        user.is_active = True
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
