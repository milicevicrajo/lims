from django import forms
from .models import Laboratory, Standard, TestingArea, TestSubject, SubDiscipline
from .models import Method
from django_select2.forms import Select2Widget, Select2MultipleWidget

class StandardForm(forms.ModelForm):
    class Meta:
        model = Standard
        fields = '__all__'

class TestingAreaForm(forms.ModelForm):
    class Meta:
        model = TestingArea
        fields = '__all__'

class TestSubjectForm(forms.ModelForm):
    class Meta:
        model = TestSubject
        fields = '__all__'      

class SubDisciplineForm(forms.ModelForm):
    testing_area = forms.ModelChoiceField(
        queryset=TestingArea.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Oblast ispitivanja"
    )

    test_subject = forms.ModelMultipleChoiceField(
        queryset=TestSubject.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Predmeti ispitivanja"
    )
    class Meta:
        model = SubDiscipline
        exclude = ['laboratory']  # Exclude the laboratory field

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and (user.is_superuser or user.role == 'admin'):
            # Superuser i admin: slobodan izbor laboratorije
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.all(),
                label="Laboratorija",
                widget=forms.Select(attrs={'class': 'form-control'}),
                required=True
            )
        else:
            # Ostali korisnici: zaključano polje (skriveno), dodeljena laboratorija
            lab = user.laboratory or user.laboratory_permissions.first()

            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.filter(id=lab.id) if lab else Laboratory.objects.none(),
                initial=lab.id if lab else None,
                label="Laboratorija",
                widget=forms.HiddenInput(),
                required=False
            )
            self.instance.laboratory = lab


class MethodForm(forms.ModelForm):
    testing_area = forms.ModelChoiceField(
        queryset=TestingArea.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Oblast ispitivanja"
    )
    
    test_subjects = forms.ModelChoiceField(
        queryset=TestSubject.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Predmeti ispitivanja"
    )
    
    standard = forms.ModelChoiceField(
        queryset=Standard.objects.all(),
        widget=Select2Widget(attrs={'class': 'select2-method'}),
        label="Standard"
    )
    standard_secondary = forms.ModelMultipleChoiceField(
        queryset=Standard.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Standard - dodatni"
    )

    class Meta:
        model = Method
        exclude = ['equipment',] 

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Ensure that user is passed to the form
        super().__init__(*args, **kwargs)

        if user and (user.is_superuser or user.role == 'admin'):
            # Superuser i admin mogu da biraju bilo koju laboratoriju
            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.all(),
                required=True,
                label="Laboratorija",
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        else:
            # Za ostale korisnike: biramo laboratoriju iz user.laboratory (ako postoji)
            # ili ako koristiš laboratory_permissions: prvi izbor iz dozvoljenih laboratorija
            lab = user.laboratory or user.laboratory_permissions.first()

            self.fields['laboratory'] = forms.ModelChoiceField(
                queryset=Laboratory.objects.filter(id=lab.id) if lab else Laboratory.objects.none(),
                initial=lab.id if lab else None,
                label="Odgovorna laboratorija",
                widget=forms.HiddenInput(),
                required=False
            )

            self.instance.laboratory = lab
