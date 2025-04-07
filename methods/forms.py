from django import forms
from .models import Laboratory, Standard, TestingArea, TestSubject, SubDiscipline
from .models import Method
from django_select2.forms import Select2Widget, Select2MultipleWidget

from django import forms
from .models import Laboratory, Standard, TestingArea, TestSubject, SubDiscipline, Method
from .helpers import select2_widget, select2_multiple_widget

# --- Standard Form ---
class StandardForm(forms.ModelForm):
    class Meta:
        model = Standard
        fields = '__all__'


# --- Testing Area Form ---
class TestingAreaForm(forms.ModelForm):
    class Meta:
        model = TestingArea
        fields = '__all__'


# --- Test Subject Form ---
class TestSubjectForm(forms.ModelForm):
    class Meta:
        model = TestSubject
        fields = '__all__'  
# --- SubDiscipline Form ---
class SubDisciplineForm(forms.ModelForm):
    testing_area = forms.ModelChoiceField(
        queryset=TestingArea.objects.all(),
        widget=select2_widget(),
        label="Oblast ispitivanja"
    )
    test_subject = forms.ModelMultipleChoiceField(
        queryset=TestSubject.objects.all(),
        widget=select2_multiple_widget(),
        label="Predmeti ispitivanja"
    )

    class Meta:
        model = SubDiscipline
        exclude = ['laboratory']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and (user.is_superuser or user.role == 'admin'):
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.all(),
                label="Laboratorija",
                widget=select2_widget(),
                required=True
            )
        else:
            lab = user.laboratory or user.laboratory_permissions.first()
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.filter(id=lab.id) if lab else Laboratory.objects.none(),
                initial=lab.id if lab else None,
                widget=forms.HiddenInput(),
                required=False
            )
            self.instance.laboratory = lab


# --- Method Form ---
class MethodForm(forms.ModelForm):
    testing_area = forms.ModelChoiceField(
        queryset=TestingArea.objects.all(),
        widget=select2_widget(),
        label="Oblast ispitivanja"
    )
    test_subjects = forms.ModelChoiceField(
        queryset=TestSubject.objects.all(),
        widget=select2_widget(),
        label="Predmet ispitivanja"
    )
    standard = forms.ModelChoiceField(
        queryset=Standard.objects.all(),
        widget=select2_widget(),
        label="Standard"
    )
    standard_secondary = forms.ModelMultipleChoiceField(
        queryset=Standard.objects.all(),
        widget=select2_multiple_widget(),
        label="Standard - dodatni",
        required=False
    )

    class Meta:
        model = Method
        exclude = ['equipment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and (user.is_superuser or user.role == 'admin'):
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.all(),
                label="Laboratorija",
                widget=select2_widget(),
                required=True
            )
        else:
            lab = user.laboratory or user.laboratory_permissions.first()
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.filter(id=lab.id) if lab else Laboratory.objects.none(),
                initial=lab.id if lab else None,
                widget=forms.HiddenInput(),
                required=False
            )
            self.instance.laboratory = lab