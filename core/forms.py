from django import forms
from .models import CustomUser, Laboratory, OrganizationalUnit, Center
from django_select2.forms import Select2MultipleWidget

class UserQuerysetMixin:
    """
    Mixin koji dinamički filtrira queryset na osnovu korisničkih prava.
    Ako je superuser, vraća sve.
    """

    def apply_user_filtering(self, user):
        from core.models import Laboratory
        from methods.models import Method
        from staff.models import Staff

        def filter_queryset(model):
            # Ako je superuser, vidi sve
            if user.is_superuser:
                return model.objects.all()

            # Ako model ima polje 'laboratory'
            if hasattr(model, '_meta') and 'laboratory' in [f.name for f in model._meta.fields]:
                # Ako korisnik ima laboratoriju dodeljenu
                if user.laboratory:
                    return model.objects.filter(laboratory=user.laboratory)
                elif user.laboratory_permissions.exists():
                    return model.objects.filter(laboratory__in=user.laboratory_permissions.all())
                else:
                    return model.objects.none()

            # Ako model ima polje 'organizational_unit'
            if hasattr(model, '_meta') and 'organizational_unit' in [f.name for f in model._meta.fields]:
                if user.laboratory:
                    return model.objects.filter(organizational_unit=user.laboratory.organizational_unit)
                elif user.laboratory_permissions.exists():
                    org_units = user.laboratory_permissions.values_list('organizational_unit', flat=True)
                    return model.objects.filter(organizational_unit__in=org_units)
                else:
                    return model.objects.none()

            # Ako model nema očekivana polja, vrati sve
            return model.objects.all()

        # Primenjujemo na polja u formi
        if 'laboratory' in self.fields:
            self.fields['laboratory'].queryset = filter_queryset(Laboratory)

        if 'method' in self.fields:
            self.fields['method'].queryset = filter_queryset(Method)

        if 'staff' in self.fields:
            self.fields['staff'].queryset = filter_queryset(Staff)



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