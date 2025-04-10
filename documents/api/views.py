from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from documents.models import Document, DocumentVersion
from documents.services import create_document, delete_document, get_documents_with_current_version, update_document, get_file_response
from .serializers import DocumentSerializer, DocumentVersionSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action


@extend_schema(tags=['Documents'])
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()  # Dodaj ovo
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        return get_documents_with_current_version(queryset)
    
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        document = self.get_object()
        status_text = toggle_document_status(document)
        return Response(
            {"message": f"Dokument je uspešno {status_text}."},
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        create_document(serializer.validated_data, self.request.user)

    def perform_update(self, serializer):
        update_document(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        delete_document(instance)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer

    @action(detail=False, methods=['post'], url_path='create-version')
    def create_version(self, request):
        document_id = request.data.get('document_id')
        document = get_object_or_404(Document, pk=document_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        version = DocumentVersion(**serializer.validated_data)
        version.document = document
        handle_document_version_creation(document, version)
        version.save()

        return Response(
            {"message": "Verzija dokumenta je uspešno kreirana."},
            status=status.HTTP_201_CREATED
        )

class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        version = self.get_object()
        return get_file_response(version)