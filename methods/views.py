from django.forms import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import Standard, TestingArea, TestSubject, SubDiscipline, Method
from .forms import StandardForm, TestingAreaForm, TestSubjectForm, SubDisciplineForm, MethodForm
from .filters import MethodFilter
from lims.mixins import LaboratoryRoleMixin
from django.shortcuts import redirect, get_object_or_404
from .services import create_standard, create_subdiscipline, delete_subdiscipline, get_method_detail_context, get_subdiscipline_methods, update_standard, delete_standard, update_subdiscipline
from equipment.filters import EquipmentFilter
from .services import (
    create_testing_area, update_testing_area, delete_testing_area,
    create_test_subject, update_test_subject, delete_test_subject
)
from .services import create_method, update_method, delete_method
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .services import update_method_equipment, get_user_equipment_queryset_for_method


# STANDARD 
@method_decorator(never_cache, name='dispatch')
class StandardListView(ListView):
    model = Standard
    template_name = 'methods/standard_list.html'
    context_object_name = 'standards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak svih standarda'
        return context


class StandardCreateView(CreateView):
    model = Standard
    form_class = StandardForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('standard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj zapis o standardu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            standard = create_standard(form.cleaned_data)
            return redirect('standard_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class StandardUpdateView(UpdateView):
    model = Standard
    form_class = StandardForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('standard_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi zapis o standardu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            update_standard(self.object, form.cleaned_data)
            return redirect('standard_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

class StandardDeleteView(DeleteView):
    model = Standard
    success_url = reverse_lazy('standard_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Standard, id=self.kwargs.get('pk'))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_standard(instance)
        return redirect(self.success_url)


# TESTING AREA and TEST SUBJECT
class TestingAreaCreateView(LoginRequiredMixin, CreateView):
    model = TestingArea
    form_class = TestingAreaForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj oblast ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            create_testing_area(form.cleaned_data)
            return redirect('testandarea_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TestingAreaUpdateView(LoginRequiredMixin, UpdateView):
    model = TestingArea
    form_class = TestingAreaForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi oblast ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            update_testing_area(self.object, form.cleaned_data)
            return redirect('testandarea_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TestingAreaDeleteView(LoginRequiredMixin, DeleteView):
    model = TestingArea

    def get_object(self, queryset=None):
        return get_object_or_404(TestingArea, id=self.kwargs.get('pk'))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_testing_area(instance)
        return redirect('testandarea_list')

class TestSubjectCreateView(LoginRequiredMixin, CreateView):
    model = TestSubject
    form_class = TestSubjectForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj predmet ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            create_test_subject(form.cleaned_data)
            return redirect('testandarea_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TestSubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = TestSubject
    form_class = TestSubjectForm
    template_name = 'generic_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi predmet ispitivanja'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            update_test_subject(self.object, form.cleaned_data)
            return redirect('testandarea_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class TestSubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = TestSubject

    def get_object(self, queryset=None):
        return get_object_or_404(TestSubject, id=self.kwargs.get('pk'))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_test_subject(instance)
        return redirect('testandarea_list')

class CombinedListView(LoginRequiredMixin, ListView):
    template_name = 'methods/testing_area_subject_list.html'
    context_object_name = 'data'

    def get_queryset(self):
        return {
            'testing_areas': TestingArea.objects.all(),
            'test_subjects': TestSubject.objects.all()
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testing_areas'] = TestingArea.objects.all()
        context['test_subjects'] = TestSubject.objects.all()
        context['title'] = 'Spisak oblasti i predmeta ispitivanja sa pripadajućim kodovima'
        return context


# SUBDISCIPLINE 
@method_decorator(never_cache, name='dispatch')
class SubDisciplineListView(LoginRequiredMixin, ListView):
    model = SubDiscipline
    template_name = 'methods/sub_discipline_list.html'
    context_object_name = 'sub_disciplines'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak poddisciplina'
        return context
    
class SubDisciplineDetailView(LoginRequiredMixin, DetailView):
    model = SubDiscipline
    template_name = 'methods/sub_discipline_detail.html'
    context_object_name = 'sub_discipline'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['methods'] = get_subdiscipline_methods(self.object)
        context['title'] = 'Spisak metoda unutar poddiscipline'
        return context


class SubDisciplineCreateView(LoginRequiredMixin, CreateView):
    form_class = SubDisciplineForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('sub_discipline_list')

    def form_valid(self, form):
        create_subdiscipline(form.cleaned_data)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kreiraj novu poddisciplinu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    
class SubDisciplineUpdateView(LoginRequiredMixin, UpdateView):
    model = SubDiscipline
    form_class = SubDisciplineForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('sub_discipline_list')

    def form_valid(self, form):
        update_subdiscipline(self.object, form.cleaned_data)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi poddisciplinu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
class SubDisciplineDeleteView(LoginRequiredMixin, DeleteView):
    model = SubDiscipline
    success_url = reverse_lazy('sub_discipline_list')

    def delete(self, request, *args, **kwargs):
        delete_subdiscipline(self.get_object().pk)
        return redirect(self.success_url)

    
# METHOD VIEWS
@method_decorator(never_cache, name='dispatch')
class MethodListView(FilterView):
    model = Method
    filterset_class = MethodFilter
    template_name = 'methods/method_list.html'
    context_object_name = 'methods'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Spisak metoda'
        return context

class MethodDetailView(DetailView):
    model = Method
    template_name = 'methods/method_detail.html'
    context_object_name = 'method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()
        context.update(get_method_detail_context(method))
        return context

        # context['standard_secondary'] = Method.standard_secondary.filter(method=method)
        return context
    
class MethodCreateView(CreateView):
    model = Method
    form_class = MethodForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('method_list')
    manual = "Polje 'Standard - dodatni' se odnosi na dodatke standardu ili u slučajevima kada se dva identična standarda imaju različite oznake može se ubaciti i drugi standard."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Formiraj novu metodu'
        context['submit_button_label'] = 'Potvrdi'
        context['manual'] = self.manual
        return context

    def form_valid(self, form):
        try:
            create_method(form.cleaned_data, self.request.user)
            return redirect('method_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    
class MethodUpdateView(LaboratoryRoleMixin, UpdateView):
    model = Method
    form_class = MethodForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('method_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi metodu'
        context['submit_button_label'] = 'Potvrdi'
        return context

    def form_valid(self, form):
        try:
            update_method(self.object, form.cleaned_data)
            return redirect('method_list')
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class MethodDeleteView(DeleteView):
    model = Method
    template_name = 'methods/method_confirm_delete.html'
    success_url = reverse_lazy('method_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Method, id=self.kwargs.get('pk'))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_method(instance)
        return redirect('method_list')


class SelectEquipmentView(DetailView):
    model = Method
    template_name = 'methods/select_equipment.html'
    context_object_name = 'method'

    def post(self, request, *args, **kwargs):
        method = self.get_object()
        action = request.POST.get('action')
        selected_equipment_id = request.POST.get('equipment_id')

        if selected_equipment_id:
            result = update_method_equipment(method, selected_equipment_id, action)

            if 'error' in result:
                return JsonResponse({'message': result['error']}, status=400)
            return JsonResponse(result)

        return JsonResponse({'message': 'Invalid request'}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_queryset = get_user_equipment_queryset_for_method(self.request.user)

        equipment_filter = EquipmentFilter(self.request.GET, queryset=equipment_queryset)
        context['filter'] = equipment_filter
        context['all_equipment'] = equipment_filter.qs
        return context
