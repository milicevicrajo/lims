from django import forms
from .models import Staff, StaffJobPosition, JobPosition, ProfessionalExperience, TrainingCourse, MembershipInInternationalOrg, Training, TrainingTests, AuthorizationType, Authorization, NoMethodAuthorization
from django_select2.forms import Select2Widget, Select2MultipleWidget
from methods.models import Method

class StaffForm(forms.ModelForm):    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum rođenja"
    )
    start_date_in_profession  = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Početak rada u struci"
    )
    start_date_in_ims = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Početak rada u IMS"
    )
    class Meta:
        model = Staff
        fields = '__all__'  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['date_of_birth'] = self.instance.date_of_birth.strftime('%Y-%m-%d')
            self.initial['start_date_in_profession'] = self.instance.start_date_in_profession.strftime('%Y-%m-%d')
            self.initial['start_date_in_ims'] = self.instance.start_date_in_ims.strftime('%Y-%m-%d')


class StaffJobPositionForm(forms.ModelForm):
    start_date  = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Početak rada u na radnom mestu"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Kraj rada u na radnom mestu",
        required=False  # This makes the field optional
    )
    class Meta:
        model = StaffJobPosition
        fields = ['staff', 'job_position', 'start_date', 'end_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')

class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = '__all__'

class ProfessionalExperienceForm(forms.ModelForm):
    class Meta:
        model = ProfessionalExperience
        fields = '__all__'

class TrainingCourseForm(forms.ModelForm):
    class Meta:
        model = TrainingCourse
        fields = '__all__'


class MembershipInInternationalOrgForm(forms.ModelForm):
    class Meta:
        model = MembershipInInternationalOrg
        fields = '__all__'

class TrainingForm(forms.ModelForm):
    methods = forms.ModelMultipleChoiceField(
        queryset=Method.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Metode",
        required = False
    )

    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    
    instructors = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Nosioci obuke",
        required = False
    )

    report_submitted = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Izveštaj podneo"
    )

    start_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Početak obuke"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Kraj obuke"
    )
    report_date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum izveštaja"
    )
    class Meta:
        model = Training
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')
            self.initial['report_date'] = self.instance.report_date.strftime('%Y-%m-%d')
class TrainingTestForm(forms.ModelForm):
    class Meta:
        model = TrainingTests
        fields = ['test']
        widgets = {
            'test': forms.FileInput(attrs={'accept': 'application/pdf'}),
        }

class AuthorizationTypeForm(forms.ModelForm):
    class Meta:
        model = AuthorizationType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class AuthorizationForm(forms.Form):
    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    methods = forms.ModelMultipleChoiceField(
        queryset=Method.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Metode"
    )
    authorization_type = forms.ModelMultipleChoiceField(
        queryset=AuthorizationType.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Ovlašćenje"
    )
    date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum dodele ovlašćenja"
    )
    class Meta:
        model = Authorization
        fields = ['staff', 'methods', 'authorization_type', 'date']

class AuthorizationUpdateForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum dodele ovlašćenja"
    )
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    method = forms.ModelChoiceField(
        queryset=Method.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Metode"
    )
    authorization_type = forms.ModelChoiceField(
        queryset=AuthorizationType.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Ovlašćenje"
    )
    class Meta:
        model = Authorization
        fields = '__all__'  # Or specify the fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%d')

class NoMethodAuthorizationForm(forms.ModelForm):
    staff = forms.ModelMultipleChoiceField(
        queryset=Staff.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Zaposleni"
    )
    date = forms.DateField(
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        label="Datum dodele ovlašćenja"
    )
    class Meta:
        model = NoMethodAuthorization
        fields = ['staff', 'authorization', 'date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:  # Check if instance is being updated
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%d')
