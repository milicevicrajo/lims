from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured

class LaboratoryRoleMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        # Superuser ima potpunu kontrolu
        if user.is_superuser:
            return True

        # Proveri da li objekat ima 'laboratory' ili 'responsible_laboratory'
        obj_lab = getattr(obj, 'laboratory', None)
        resp_lab = getattr(obj, 'responsible_laboratory', None)

        if not obj_lab and not resp_lab:
            raise ImproperlyConfigured(
                "Model nije kompatibilan sa LaboratoryRoleMixin. "
                "Mora imati atribut 'laboratory' ili 'responsible_laboratory'."
            )

        # Ako korisnik ima ulogu "staff" ili "admin", proveri da li ima dozvolu za laboratoriju
        if user.role in ['staff', 'admin']:
            user_labs = user.laboratory_permissions.all()
            return (obj_lab in user_labs) or (resp_lab in user_labs)

        return False

class LaboratoryPermissionMixin:
    def filter_by_user_permissions(self, queryset):
        # Ako je korisnik superuser, dozvoljavamo mu da vidi sve
        if self.request.user.is_superuser:
            return queryset

        # Ako korisnik nije autentifikovan, vraćamo prazan queryset
        if not self.request.user.is_authenticated:
            return queryset.none()

        # Proveravamo da li korisnik ima dozvolu za laboratorije
        if hasattr(self.request.user, 'laboratory_permissions'):
            # Filtriramo stavke na osnovu laboratorija u kojima korisnik ima dozvole
            return queryset.filter(
                Q(laboratory__in=self.request.user.laboratory_permissions.all())
            )

        # Ako korisnik nema laboratorijske dozvole, vraćamo prazan queryset
        return queryset.none()

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_permissions(queryset)
    
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []  # Ovo treba redefinisati u naslednicima

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        raise PermissionDenied("Nemate dozvolu za ovu akciju.")


class SuperuserOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['superuser']


class AdminOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['admin']


class QualityOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['quality']


class StaffOrAboveMixin(RoleRequiredMixin):
    allowed_roles = ['superuser', 'admin', 'quality', 'staff']


class QualityOrSuperuserMixin(RoleRequiredMixin):
    allowed_roles = ['superuser', 'quality']
