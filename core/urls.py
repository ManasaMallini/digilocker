from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/documents/', include('documents.urls')),
    
    # Frontend Routes (Serving HTML Templates)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('verify/', TemplateView.as_view(template_name='verify.html'), name='verify'),
    path('share/<uuid:token>/', TemplateView.as_view(template_name='share.html'), name='share_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
