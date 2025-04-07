from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin

from quality.services import get_empty_pt_scheme_method_formset, get_pt_scheme_fields, process_pt_scheme_form
from .models import PTScheme, PTSchemeMethod, ControlTesting, ControlTestingMethod, MeasurementUncertainty
from .forms import PTSchemeMethodForm, SelectMethodCountForm, PTSchemeForm, ControlTestingMethodForm, ControlTestingForm, MeasurementUncertaintyForm

# PT SCHEME 
@method_decorator(never_cache, name='dispatch')
class PTSchemeListView(LoginRequiredMixin, ListView):
    model = PTScheme
    template_name = 'quality/pt_scheme_list.html'
    context_object_name = 'pt_schemes'

class PTSchemeDetailView(DetailView):
    model = PTScheme
    template_name = 'quality/pt_scheme_detail.html'
    context_object_name = 'pt_scheme'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()
        
        context['fields'] = get_pt_scheme_fields(self.object)
        context['methods'] = PTSchemeMethod.objects.filter(pt_scheme=self.object)
        return context

class PTSchemeCreateView(View):
    template_name = 'quality/pt_scheme_form.html'

    def get(self, request, *args, **kwargs):
        number_of_methods = request.GET.get('number_of_methods')

        if number_of_methods:
            number_of_methods = int(number_of_methods)
            # Ovde dodaš user:
            scheme_form = PTSchemeForm(user=request.user)
            method_formset = get_empty_pt_scheme_method_formset(number_of_methods)

            return render(request, self.template_name, {
                'scheme_form': scheme_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })

        method_count_form = SelectMethodCountForm()
        return render(request, 'quality/select_method_count.html', {'method_count_form': method_count_form})

    def post(self, request, *args, **kwargs):
        number_of_methods = request.POST.get('number_of_methods')

        if number_of_methods:
            number_of_methods = int(number_of_methods)

            # Prosledi request.user ovde
            pt_scheme, scheme_form, method_formset = process_pt_scheme_form(
                request.POST,
                request.FILES,
                number_of_methods,
                user=request.user  # <--- DODAJ USER OVDE
            )

            if pt_scheme:
                return redirect(reverse_lazy('pt_scheme_list'))

            return render(request, self.template_name, {
                'scheme_form': scheme_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })

        return redirect('select_method_count')

class PTSchemeUpdateView(LoginRequiredMixin, UpdateView):    
    model = PTScheme
    form_class = PTSchemeForm
    template_name = 'generic_form.html'
    context_object_name = 'pt_scheme'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ispravi osnovne podatke PT aktivnosti'
        context['submit_button_label'] = 'Potvrdi'
        return context
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('pt_scheme_list')


class PTSchemeMethodUpdateView(LoginRequiredMixin, UpdateView):
    model = PTSchemeMethod
    fields = ['pt_scheme', 'method', 'number_of_participants', 'z_score', 'staff', 'measures_taken']
    template_name = 'generic_form.html'
    context_object_name = 'pt_scheme_method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pt_scheme_method = self.get_object()
        pt_scheme = pt_scheme_method.pt_scheme
        context['title'] = f'Ispravi podatke o metodi unutar šeme {pt_scheme}'
        context['submit_button_label'] = 'Potvrdi'
        return context
    

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('pt_scheme_list')
class PTSchemeDeleteView(LoginRequiredMixin, DeleteView):
    model = PTScheme
    template_name = 'generic_form.html'
    success_url = reverse_lazy('pt_scheme_list')

    def get_object(self, queryset=None):
        obj = PTScheme.objects.get(id=self.kwargs.get('pk'))
        return obj

# CONTROL TESTING
@method_decorator(never_cache, name='dispatch')
class ControlTestingListView(LoginRequiredMixin, ListView):
    model = ControlTesting
    template_name = 'quality/control_testing_list.html'
    context_object_name = 'control_testings'


class ControlTestingDetailView(DetailView):
    model = ControlTesting
    template_name = 'quality/control_testing_detail.html'
    context_object_name = 'control_test'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['methods'] = ControlTestingMethod.objects.filter(control_test=self.object)
        return context

from .services import create_control_testing_method_formset, create_control_testing, create_measurement_uncertainty, delete_measurement_uncertainty, update_control_testing, delete_control_testing, update_measurement_uncertainty

class ControlTestingCreateView(View):
    template_name = 'quality/control_testing_form.html'

    def get(self, request, *args, **kwargs):
        if 'number_of_methods' in request.GET:
            number_of_methods = int(request.GET['number_of_methods'])
            ControlTestingMethodFormSet = create_control_testing_method_formset(number_of_methods)
            return render(request, self.template_name, {
                'control_form': ControlTestingForm(),
                'method_formset': ControlTestingMethodFormSet(),
                'number_of_methods': number_of_methods,
            })

        return render(request, 'quality/select_ct_method_count.html', {'method_count_form': SelectMethodCountForm()})

    def post(self, request, *args, **kwargs):
        if 'number_of_methods' in request.POST:
            number_of_methods = int(request.POST['number_of_methods'])
            control_testing, control_form, method_formset = create_control_testing(request.POST, request.FILES, number_of_methods)

            if control_testing:
                return redirect(reverse_lazy('control_testing_list'))

            return render(request, self.template_name, {
                'control_form': control_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })

        return redirect('select_method_count')


class ControlTestingUpdateView(UpdateView):
    model = ControlTesting
    form_class = ControlTestingForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('control_testing_list')

    def form_valid(self, form):
        success, errors = update_control_testing(self.get_object(), self.request.POST, self.request.FILES)
        if success:
            return super().form_valid(form)
        else:
            form.add_error(None, errors)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'updating': True,
            'submit_button_label': 'Potvrdi',
            'title': f'Ispravi podatke o metodi unutar kontrolnog ispitivanja {self.get_object()}'
        })
        return context


class ControlTestingDeleteView(LoginRequiredMixin, DeleteView):
    model = ControlTesting
    template_name = 'quality/control_testing_confirm_delete.html'
    success_url = reverse_lazy('control_testing_list')

    def delete(self, request, *args, **kwargs):
        delete_control_testing(self.kwargs.get('pk'))
        return redirect(self.success_url)



class ControlTestingDeleteView(LoginRequiredMixin, DeleteView):
    model = ControlTesting
    template_name = 'quality/control_testing_confirm_delete.html'
    success_url = reverse_lazy('control_testing_list')

    def get_object(self, queryset=None):
        obj = ControlTesting.objects.get(id=self.kwargs.get('pk'))
        return obj

# MEASUREMENT UNCERTAINTY
class MeasurementUncertaintyListView(LoginRequiredMixin, ListView):
    model = MeasurementUncertainty
    template_name = 'quality/measurement_uncertainty_list.html'
    context_object_name = 'measurement_uncertainties'

class MeasurementUncertaintyCreateView(LoginRequiredMixin, CreateView):
    model = MeasurementUncertainty
    form_class = MeasurementUncertaintyForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('measurement_uncertainties_list')

    def form_valid(self, form):
        # Cleaned data iz forme
        create_measurement_uncertainty(form.cleaned_data, self.request.user)
        return super().form_valid(form)


class MeasurementUncertaintyUpdateView(LoginRequiredMixin, UpdateView):
    model = MeasurementUncertainty
    form_class = MeasurementUncertaintyForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('measurement_uncertainties_list')

    def form_valid(self, form):
        update_measurement_uncertainty(self.object, form.cleaned_data)
        return super().form_valid(form)


class MeasurementUncertaintyDeleteView(LoginRequiredMixin, DeleteView):
    model = MeasurementUncertainty
    template_name = 'quality/measurement_uncertainty_confirm_delete.html'
    success_url = reverse_lazy('measurement_uncertainties_list')

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_measurement_uncertainty(instance)
        return super().delete(request, *args, **kwargs)
