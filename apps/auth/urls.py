from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.auth.views import (
    CreateManagerView,
    RecoveryPasswordRequestView,
    RecoveryPasswordView,
    UserActivateView,
    UserSetPasswordView,
)
from apps.users.views import MeView

urlpatterns = [
    path('/login', TokenObtainPairView.as_view(), name='auth_login'),
    path('/refresh', TokenRefreshView.as_view(), name='auth_refresh'),
    path('/me', MeView.as_view(), name='auth_me'),
    path('/recovery', RecoveryPasswordRequestView.as_view(), name='auth_recovery_request'),
    path('/recovery/<str:token>', RecoveryPasswordView.as_view(), name='auth_recovery'),
    path('/create-manager', CreateManagerView.as_view(), name='create_manager'),
    path('/send-activation', UserActivateView.as_view(), name='send_activation'),
    path('/activate/<str:token>', UserSetPasswordView.as_view(), name='auth_activate'),
]