"""
Accounts URLs - Authentication and User Management API Routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, LogoutView, RegisterView,
    UserViewSet, TenantMembershipViewSet, AgencyMembershipViewSet,
    ClientMembershipViewSet, NotificationPreferenceView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tenant-memberships', TenantMembershipViewSet, basename='tenantmembership')
router.register(r'agency-memberships', AgencyMembershipViewSet, basename='agencymembership')
router.register(r'client-memberships', ClientMembershipViewSet, basename='clientmembership')

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Notification preferences
    path('notification-preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),

    # Router URLs
    path('', include(router.urls)),
]
