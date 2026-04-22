import random
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from .models import Profile
from logs.models import ActivityLog

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Simulate sending OTP
        otp = str(random.randint(100000, 999999))
        user.otp_secret = otp
        user.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action='VERIFY',
            details=f"Registration successful. Simulated OTP: {otp}"
        )
        print(f"DEBUG: Simulated OTP for {user.email}: {otp}")

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        profile_data = self.request.data.get('profile')
        user = serializer.save()
        if profile_data:
            profile = user.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

class VerifyOTPView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        otp = request.data.get('otp')
        user = request.user
        if user.otp_secret == otp:
            user.is_verified = True
            user.otp_secret = None
            user.save()
            ActivityLog.objects.create(user=user, action='VERIFY', details="OTP verified successfully.")
            return Response({"message": "Verification successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            ActivityLog.objects.create(user=user, action='LOGIN', details="User logged in via JWT.")
        return response

class ActivityLogView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        logs = ActivityLog.objects.filter(user=request.user).values('action', 'timestamp', 'details')[:10]
        return Response(logs)

class AdminUserListView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        users = User.objects.all().values('id', 'email', 'is_verified', 'role', 'date_joined')
        return Response(users)

class SystemStatsView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        from documents.models import Document
        return Response({
            "total_users": User.objects.count(),
            "total_documents": Document.objects.count(),
            "total_storage": sum(d.file_size for d in Document.objects.all()),
            "verified_users": User.objects.filter(is_verified=True).count()
        })
