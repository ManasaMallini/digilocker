from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserProfileView, VerifyOTPView, MyTokenObtainPairView, ActivityLogView, AdminUserListView, SystemStatsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('logs/', ActivityLogView.as_view(), name='activity_logs'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_users'),
    path('admin/stats/', SystemStatsView.as_view(), name='admin_stats'),
]
