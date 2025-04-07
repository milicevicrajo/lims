from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from documents.services import get_documents_with_current_version, handle_document_version_creation
from .models import Document, DocumentVersion
from .forms import DocumentForm, DocumentVersionForm
from django_filters.views import FilterView
from .filters import DocumentFilter
from django.contrib import messages
from lims.mixins import QualityOrSuperuserMixin

from .services import get_documents_with_current_version, get_file_response

class DocumentListView(LoginRequiredMixin, FilterView):
    model = Document
    template_name = 'documentation/document_list.html'
    context_object_name = 'documents'
    filterset_class = DocumentFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = get_documents_with_current_version(context['documents'])
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dodaj novi dokument'
        context['submit_button_label'] = 'Potvrdi'
        return context

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('document-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Izmeni dokument'
        context['submit_button_label'] = 'Potvrdi'
        return context

from .services import toggle_document_status

class DocumentToggleStatusView(QualityOrSuperuserMixin, View):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        status = toggle_document_status(document)
        messages.success(request, f"Dokument je uspešno {status}.")
        return redirect('document-detail', pk=pk)


from .services import handle_document_version_creation

class DocumentVersionCreateView(LoginRequiredMixin, CreateView):
    model = DocumentVersion
    form_class = DocumentVersionForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('document_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj nov verziju dokumenta'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def form_valid(self, form):
        document = get_object_or_404(Document, pk=self.kwargs['document_id'])
        form.instance.document = document
        handle_document_version_creation(document, form)
        return super().form_valid(form)


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
        return get_file_response(version)

