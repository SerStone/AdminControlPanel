from django.urls import path

from apps.orders.views import (
    AddMangerToOrder,
    CommentCreateView,
    CommentDeleteView,
    GroupCreateView,
    OrderListCreateView,
    OrderRetrieveUpdateDestroyView,
    OrderStatsView,
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order_list_create'),
    path('/groups', GroupCreateView.as_view(), name='group_create'),
    path('/stats', OrderStatsView.as_view(), name='order-stats'),
    path('/<int:pk>/', OrderRetrieveUpdateDestroyView.as_view(), name='order-detail'),
    path('/<int:pk>/mng_to_ord', AddMangerToOrder.as_view(), name='manager_to_order'),
    path('/<int:pk>/add_comment', CommentCreateView.as_view(), name='add_comment'),
    path('/<int:pk>/comment/<int:comment_id>', CommentDeleteView.as_view(), name='delete_comment'),
]
