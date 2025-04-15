from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from core.dataclasses.order_dataclass import OrderDataClass
from core.dataclasses.user_dataclass import UserDataClass

from apps.orders.models import OrderModel


class IsManager(BasePermission):
    def has_permission(self, request: Request, view):
        user: UserDataClass = request.user
        order_id = view.kwargs.get('pk')

        if not order_id:
            raise NotFound({"error": "Order ID is required."})

        try:
            order: OrderDataClass = OrderModel.objects.get(pk=order_id)

            if user.is_superuser:
                return True

            if order.manager is None:
                return True

            if order.manager.id == user.id:
                return True

            raise PermissionDenied({"error": "You are not allowed to manage this order."})

        except OrderModel.DoesNotExist:
            raise NotFound({"error": "Order not found."})


