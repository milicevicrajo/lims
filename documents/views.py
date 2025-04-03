from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Document, DocumentVersion
from .forms import DocumentForm, DocumentVersionForm
from django_filters.views import FilterView
from .filters import DocumentFilter
from django.contrib import messages
from lims.mixins import QualityOrSuperuserMixin

class DocumentListView(LoginRequiredMixin, FilterView):
    model = Document
    template_name = 'documentation/document_list.html'
    context_object_name = 'documents'
    filterset_class = DocumentFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for doc in context['documents']:  # ovo je self.object_list tj. filtrirani queryset
            doc.current_version = doc.versions.filter(is_current=True).first()
        return context

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documentation/document_detail.html'
    context_object_name = 'document'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('document_list')


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documentation/document_form.html'
    success_url = reverse_lazy('document-list')

class DocumentToggleStatusView(QualityOrSuperuserMixin, View):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        document.is_active = not document.is_active
        document.save()
        status = "aktiviran" if document.is_active else "deaktiviran"
        messages.success(request, f"Dokument je uspešno {status}.")
        return redirect('document-detail', pk=pk)



class DocumentVersionCreateView(LoginRequiredMixin, CreateView):
    model = DocumentVersion
    form_class = DocumentVersionForm
    template_name = 'generic_form.html'

    def form_valid(self, form):
        document = get_object_or_404(Document, pk=self.kwargs['document_id'])
        form.instance.document = document

        # Ako je ovo prva verzija → postavi kao current
        if not DocumentVersion.objects.filter(document=document).exists():
            form.instance.is_current = True
        elif form.cleaned_data.get('is_current'):
            # Ako je korisnik označio da je ova verzija važeća → deaktiviraj sve druge
            DocumentVersion.objects.filter(document=document).update(is_current=False)
            form.instance.is_current = True
        else:
            form.instance.is_current = False

        return super().form_valid(form)
    success_url = reverse_lazy('document_list')

class DocumentVersionListView(LoginRequiredMixin, ListView):
    model = DocumentVersion
    template_name = 'documentation/documentversion_list.html'
    context_object_name = 'versions'

    def get_queryset(self):
        document = get_object_or_404(Document, pk=self.kwargs['document_id'])
        return DocumentVersion.objects.filter(document=document).order_by('-issued_date')


from django.http import FileResponse
import os

class DownloadDocumentView(LoginRequiredMixin, DetailView):
    model = DocumentVersion

    def get(self, request, *args, **kwargs):
        version = self.get_object()
        return FileResponse(version.file.open(), as_attachment=True, filename=os.path.basename(version.file.name))

