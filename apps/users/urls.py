from django.urls import path

from .views import AdminToUserView, UserBlockView, UserCreateView, UserToAdminView, UserUnBlockView

urlpatterns = [
    path('', UserCreateView.as_view(), name='user_create'),
    path('/<int:pk>/to_admin', UserToAdminView.as_view(), name='user_to_admin'),
    path('/<int:pk>/to_user', AdminToUserView.as_view(), name='admin_to_user'),
    path('/<int:pk>/block', UserBlockView.as_view(), name='user_block'),
    path('/<int:pk>/unblock', UserUnBlockView.as_view(), name='user_unblock'),
]