import uuid
import hashlib
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='user_documents/%Y/%m/%d/')
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(help_text="File size in bytes", default=0)
    file_hash = models.CharField(max_length=64, blank=True, null=True) # Digital Fingerprint
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_encrypted = models.BooleanField(default=False) 
    expiry_date = models.DateField(null=True, blank=True)
    security_level = models.CharField(max_length=20, choices=(('normal', 'Normal'), ('high', 'High Security')), default='normal')

    def save(self, *args, **kwargs):
        if self.file and not self.file_hash:
            sha256_hash = hashlib.sha256()
            for chunk in self.file.chunks():
                sha256_hash.update(chunk)
            self.file_hash = sha256_hash.hexdigest()
        super().save(*args, **kwargs)

    def is_near_expiry(self):
        from django.utils import timezone
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days < 30
        return False

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

class ShareLink(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='share_links')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True) # Secure Access
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_expired(self):
        from django.utils import timezone
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def __str__(self):
        return f"Share link for {self.document.title}"
