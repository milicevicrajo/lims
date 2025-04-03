from django import forms
from .models import CustomUser, Laboratory, OrganizationalUnit, Center
from django_select2.forms import Select2MultipleWidget

class CenterForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = ['name', 'code']

class OrganizationalUnitForm(forms.ModelForm):
    class Meta:
        model = OrganizationalUnit
        fields = ['name', 'code', 'center']

class LaboratoryForm(forms.ModelForm):
    class Meta:
        model = Laboratory
        fields = ['name', 'organizational_unit']


class CustomUserCreationForm(forms.ModelForm):
    
    laboratory_permissions = forms.ModelMultipleChoiceField(
        queryset=Laboratory.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'select2-method'}),
        label="Dozvole za laboratorije"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'laboratory', 'laboratory_permissions', 'role', 'username', 'email', 'password']


    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['password'].widget = forms.PasswordInput()

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            self.save_m2m()  # This is crucial to save ManyToMany relations
        return user