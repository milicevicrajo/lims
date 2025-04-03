from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class Center(models.Model):
    name = models.CharField(_("Naziv centra"), max_length=100)
    code = models.CharField(_("Šifra centra"), max_length=2, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class OrganizationalUnit(models.Model):
    name = models.CharField(_("Naziv"), max_length=100)
    code = models.CharField(_("Šifra"), max_length=10, unique=True)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='units')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Laboratory(models.Model):
    name = models.CharField(_("Naziv laboratorije"), max_length=100)
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE, related_name='laboratories')

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Administrator laboratorije'),
        ('quality', 'Kontrolor kvaliteta'),
        ('staff', 'Osoblje'),
        ('viewer', 'Pregled'),
    ]

    session_key = models.CharField(max_length=40, null=True, blank=True)
    first_name = models.CharField(_("Ime"), max_length=20)
    last_name = models.CharField(_("Prezime"), max_length=20)
    role = models.CharField(_("Uloga"), max_length=20, choices=ROLE_CHOICES, default='staff')

    laboratory = models.ForeignKey(
        Laboratory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users', 
        verbose_name=_("Laboratorija")
    )
    laboratory_permissions = models.ManyToManyField(
        Laboratory, 
        related_name='authorized_users', 
        verbose_name=_("Dozvole za laboratorije")
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("Grupe"),
        blank=True,
        help_text=_("Grupe kojima korisnik pripada. Korisnik preuzima sve dozvole iz grupa."),
        related_name="ims_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("Dozvole korisnika"),
        blank=True,
        help_text=_("Specifične dozvole za ovog korisnika."),
        related_name="ims_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

