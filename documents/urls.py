from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, DocumentViewSet, ShareDocumentView, PublicDownloadView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/share/', ShareDocumentView.as_view(), name='share_document'),
    path('public/share/<uuid:token>/', PublicDownloadView.as_view(), name='public_download'),
]
