

from documents.models import DocumentVersion


def get_documents_with_current_version(documents):
    for doc in documents:
        doc.current_version = doc.versions.filter(is_current=True).first()
    return documents

def handle_document_version_creation(document, form):
    if not DocumentVersion.objects.filter(document=document).exists():
        form.instance.is_current = True
    elif form.cleaned_data.get('is_current'):
        DocumentVersion.objects.filter(document=document).update(is_current=False)
        form.instance.is_current = True
    else:
        form.instance.is_current = False

def toggle_document_status(document):
    document.is_active = not document.is_active
    document.save()
    return "aktiviran" if document.is_active else "deaktiviran"

from django.http import FileResponse
import os

def get_file_response(version):
    return FileResponse(version.file.open(), as_attachment=True, filename=os.path.basename(version.file.name))
