from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
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
        
        fields = [
            (field.verbose_name, getattr(method, field.name))
            for field in PTScheme._meta.fields
            if not field.name.startswith('_') and field.name != 'id'
        ]
        
        context['fields'] = fields
        context['methods'] = PTSchemeMethod.objects.filter(pt_scheme=self.object)
        return context

class PTSchemeCreateView(View):
    template_name = 'quality/pt_scheme_form.html'

    def get(self, request, *args, **kwargs):
        # Check if the user has already submitted the number of methods
        if 'number_of_methods' in request.GET:
            number_of_methods = int(request.GET['number_of_methods'])
            # Create the formset using the helper function
            PTSchemeMethodFormSet = create_pt_scheme_method_formset(number_of_methods)
            method_formset = PTSchemeMethodFormSet()
            scheme_form = PTSchemeForm()
            
            return render(request, self.template_name, {
                'scheme_form': scheme_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })
        
        # Show the method count selection form
        method_count_form = SelectMethodCountForm()
        return render(request, 'quality/select_method_count.html', {'method_count_form': method_count_form})

    def post(self, request, *args, **kwargs):
        print("POST request received.")
        
        # Handle the PT scheme form and the formset after method count has been selected
        if 'number_of_methods' in request.POST:
            number_of_methods = int(request.POST['number_of_methods'])
            print(f"Number of methods (POST): {number_of_methods}")
            
            # Create the formset using the helper function
            PTSchemeMethodFormSet = create_pt_scheme_method_formset(number_of_methods)
            scheme_form = PTSchemeForm(request.POST, request.FILES)
            method_formset = PTSchemeMethodFormSet(request.POST, request.FILES)
            
            if scheme_form.is_valid() and method_formset.is_valid():
                print("Both forms are valid. Saving the PT Scheme and Methods.")
                pt_scheme = scheme_form.save()
                
                # Set the instance of the formset to the saved PT scheme
                method_formset.instance = pt_scheme
                method_formset.save()
                
                return redirect(reverse_lazy('pt_scheme_list'))  # Adjust this to your URL
            else:
                print("Form validation failed.")
                print(f"Scheme form errors: {scheme_form.errors}")
                print(f"Method formset errors: {method_formset.errors}")
            
            return render(request, self.template_name, {
                'scheme_form': scheme_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })

        # If the number_of_methods is missing, redirect to the method count form
        print("Number of methods not found in POST request.")
        return redirect('select_method_count')

# Helper function to create the formset with the desired number of forms
def create_pt_scheme_method_formset(number_of_methods):
    return inlineformset_factory(
        PTScheme, PTSchemeMethod,
        form=PTSchemeMethodForm,
        extra=number_of_methods,  # Pass the number of extra forms here
        can_delete=True  # Optional: allow deletion of forms
    )
   
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

class ControlTestingCreateView(View):
    template_name = 'quality/control_testing_form.html'

    def get(self, request, *args, **kwargs):
        # Check if the user has already submitted the number of methods
        if 'number_of_methods' in request.GET:
            number_of_methods = int(request.GET['number_of_methods'])
            
            # Create the formset using the helper function
            ControlTestingMethodFormSet = create_control_testing_method_formset(number_of_methods)
            method_formset = ControlTestingMethodFormSet()
            control_form = ControlTestingForm()
            
            return render(request, self.template_name, {
                'control_form': control_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })
        
        # Show the method count selection form
        method_count_form = SelectMethodCountForm()
        return render(request, 'quality/select_ct_method_count.html', {'method_count_form': method_count_form})

    def post(self, request, *args, **kwargs):
        # Handle the ControlTesting form and the formset after method count has been selected
        if 'number_of_methods' in request.POST:
            number_of_methods = int(request.POST['number_of_methods'])
            
            # Create the formset using the helper function
            ControlTestingMethodFormSet = create_control_testing_method_formset(number_of_methods)
            control_form = ControlTestingForm(request.POST, request.FILES)
            method_formset = ControlTestingMethodFormSet(request.POST, request.FILES)
            
            if control_form.is_valid() and method_formset.is_valid():
                control_testing = control_form.save()
                
                # Set the instance of the formset to the saved control testing
                method_formset.instance = control_testing
                method_formset.save()
                
                return redirect(reverse_lazy('control_testing_list'))  # Adjust this to your URL
            
            return render(request, self.template_name, {
                'control_form': control_form,
                'method_formset': method_formset,
                'number_of_methods': number_of_methods,
            })

        # Redirect back to the method count form if something goes wrong
        return redirect('select_method_count')

def create_control_testing_method_formset(number_of_methods):
    return inlineformset_factory(
        ControlTesting, ControlTestingMethod,
        form=ControlTestingMethodForm,
        extra=number_of_methods,
        can_delete=True  # Optional: allow form deletion
    )

class ControlTestingUpdateView(UpdateView):
    model = ControlTesting
    form_class = ControlTestingForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('control_testing_list')  # Adjust this to your URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['updating'] = True  # You can use this in the template to show it's an update
        context['submit_button_label'] = 'Potvrdi'
        context['title'] = f'Ispravi podatke o metodi unutar kontrolnog ispitivanja {self.get_object()}'
        return context


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

class MeasurementUncertaintyUpdateView(LoginRequiredMixin, UpdateView):
    model = MeasurementUncertainty
    form_class = MeasurementUncertaintyForm
    template_name = 'generic_form.html'
    success_url = reverse_lazy('measurement_uncertainties_list')

class MeasurementUncertaintyDeleteView(LoginRequiredMixin, DeleteView):
    model = MeasurementUncertainty
    template_name = 'quality/measurement_uncertainty_confirm_delete.html'
    success_url = reverse_lazy('measurement_uncertainties_list')

    def get_object(self, queryset=None):
        obj = MeasurementUncertainty.objects.get(id=self.kwargs.get('pk'))
        return obj