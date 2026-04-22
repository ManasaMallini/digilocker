from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('UPLOAD', 'File Upload'),
        ('DOWNLOAD', 'File Download'),
        ('SHARE', 'File Share'),
        ('DELETE', 'File Delete'),
        ('VERIFY', 'Email/OTP Verification'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
