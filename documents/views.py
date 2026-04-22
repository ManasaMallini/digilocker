from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Document, Category, ShareLink
from .serializers import DocumentSerializer, CategorySerializer, ShareLinkSerializer
from logs.models import ActivityLog

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'category__name']
    ordering_fields = ['uploaded_at', 'title']

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        doc = serializer.save(user=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action='UPLOAD',
            details=f"Uploaded document: {doc.title}"
        )

    def perform_destroy(self, instance):
        title = instance.title
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action='DELETE',
            details=f"Deleted document: {title}"
        )

class ShareDocumentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            document = Document.objects.get(pk=pk, user=request.user)
            expires_in_days = request.data.get('expires_in', 7)
            password = request.data.get('password') # Optional Password
            expires_at = timezone.now() + timezone.timedelta(days=int(expires_in_days))
            
            share_link = ShareLink.objects.create(
                document=document,
                expires_at=expires_at,
                password=password
            )
            
            ActivityLog.objects.create(
                user=request.user,
                action='SHARE',
                details=f"Generated secure share link for {document.title}"
            )
            
            return Response({
                "token": share_link.token,
                "expires_at": share_link.expires_at,
                "share_url": f"/share/{share_link.token}/",
                "protected": True if password else False
            }, status=status.HTTP_201_CREATED)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

class PublicDownloadView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        try:
            share_link = ShareLink.objects.get(token=token, is_active=True)
            if share_link.is_expired():
                return Response({"error": "Link expired"}, status=status.HTTP_403_FORBIDDEN)
            if share_link.password:
                return Response({"protected": True}, status=status.HTTP_200_OK)
            return self._serve_file(share_link)
        except ShareLink.DoesNotExist:
            return Response({"error": "Invalid link"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, token):
        try:
            share_link = ShareLink.objects.get(token=token, is_active=True)
            password = request.data.get('password')
            if share_link.password and share_link.password != password:
                return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
            return self._serve_file(share_link)
        except ShareLink.DoesNotExist:
            return Response({"error": "Invalid link"}, status=status.HTTP_404_NOT_FOUND)

    def _serve_file(self, share_link):
        share_link.views_count += 1
        share_link.save()
        doc = share_link.document
        return Response({
            "title": doc.title,
            "file_url": doc.file.url,
            "file_type": doc.file_type,
            "file_hash": doc.file_hash
        })
