from django.contrib.auth import get_user_model
from django.db.models import Count, F, Value
from django.db.models.functions import Coalesce

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.enums import StatusEnum
from core.permissions.is_manager import IsManager

from apps.auth.serializers import EmailSerializer
from apps.orders.filters import NoneIfEmpty, NullsLastOrderingFilter, OrderFilter
from apps.orders.models import CommentModel, GroupModel, OrderModel
from apps.orders.serializers import CommentSerializer, GroupSerializer, OrderSerializer

UserModel = get_user_model()


class GroupCreateView(ListCreateAPIView):
    queryset = GroupModel.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class OrderListCreateView(ListCreateAPIView):
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.filterset_class(self.request.GET, queryset=queryset, request=self.request)
        qs = filterset.qs

        ordering = self.request.GET.getlist('order') or self.request.GET.getlist('ordering')
        if ordering:
            f_ordering = []
            for field in ordering:
                desc = False
                if field.startswith('-'):
                    field = field[1:]
                    desc = True

                if field in ['name', 'surname', 'email', 'phone', 'course_type', 'course_format', 'course']:
                    expr = Coalesce(
                        NoneIfEmpty(field),
                        Value(None)
                    )
                else:
                    expr = F(field)

                f_ordering.append(expr.desc(nulls_last=True) if desc else expr.asc(nulls_last=True))

            qs = qs.order_by(*f_ordering)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if request.query_params.get('all') == 'true':
            serializer = self.get_serializer(queryset, many=True)
            return Response({'data': serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def update_dubbing_status(self):
        from django.db.models import Count

        duplicates = (
            OrderModel.objects
            .exclude(email="")
            .values('email')
            .annotate(email_count=Count('id'))
            .filter(email_count__gt=1)
        )
        duplicate_emails = [item['email'] for item in duplicates]
        OrderModel.objects.filter(email__in=duplicate_emails).exclude(status="Dubbing").update(status="Dubbing")


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated(), IsManager()]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddMangerToOrder(GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = (IsAdminUser,)

    def post(self, request, pk):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = get_user_model()
        try:
            user = user.objects.get(email=email)
        except user.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = OrderModel.objects.get(pk=pk)
        except OrderModel.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.admin = user
        order.save()
        return Response({"message": "User promoted to admin successfully"}, status=status.HTTP_200_OK)


class OrderStatsView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        status_counts = (
            OrderModel.objects
            .values('status')
            .annotate(count=Count('id'))
        )

        total = OrderModel.objects.count()

        stats = {status.value: 0 for status in StatusEnum}
        stats['null'] = 0
        for entry in status_counts:
            status = entry['status']
            count = entry['count']
            if status is None:
                stats['null'] = count
            else:
                stats[status] = count

        return Response({
            'total': total,
            **stats
        })


class RemoveMangerToOrder(GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = (IsManager,)

    def post(self, request, pk):
        data = self.request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = get_user_model()
        try:
            user = user.objects.get(email=email)
        except user.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = OrderModel.objects.get(pk=pk)
        except OrderModel.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.admin = user
        order.save()
        return Response({"message": "User promoted to admin successfully"}, status=status.HTTP_200_OK)


class CommentCreateView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(OrderModel, pk=pk)

        if order.manager and order.manager != request.user:
            return Response({"error": "You leave comment on this order."}, status=status.HTTP_403_FORBIDDEN)

        if not order.manager:
            order.manager = request.user

        if order.status in [None, "New"]:
            order.status = "In work"

        order.save()

        comment = CommentModel.objects.create(
            order=order,
            author=request.user,
            text=request.data.get("text")
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class CommentDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, comment_id):
        order = get_object_or_404(OrderModel, pk=pk)
        comment = get_object_or_404(CommentModel, id=comment_id, order=order)

        if request.user != order.manager and not request.user.is_superuser:
            return Response({"error": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)