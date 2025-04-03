from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Laboratory
from methods.models import Method

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Laboratory
from methods.models import Method

class DocumentType(models.Model):
    name = models.CharField(_("Naziv tipa dokumenta"), max_length=100, unique=True)  # npr. "Politika", "Procedura"
    is_record = models.BooleanField(_("Da li je zapis"), default=False)

    class Meta:
        verbose_name = _("Tip dokumenta")
        verbose_name_plural = _("Tipovi dokumenata")

    def __str__(self):
        return self.name

class Document(models.Model):
    code = models.CharField(_("Oznaka dokumenta"), max_length=50, unique=True)  # npr. "PR-001"
    title = models.CharField(_("Naziv dokumenta"), max_length=255)
    type = models.ForeignKey(DocumentType, verbose_name=_("Tip dokumenta"), on_delete=models.PROTECT)
    description = models.TextField(_("Opis"), blank=True)
    related_methods = models.ManyToManyField('methods.Method', verbose_name=_("Povezane metode"), blank=True)
    related_equipment = models.ManyToManyField('equipment.Equipment', verbose_name=_("Povezana oprema"), blank=True)
    laboratory = models.ForeignKey(
        'core.Laboratory',
        verbose_name=_("Laboratorija"),
        on_delete=models.PROTECT,
        null=True,
        blank=True  # <-- dodaj ovo
    )
    is_active = models.BooleanField(_("Aktivan"), default=True)
    created_at = models.DateTimeField(_("Datum kreiranja"), auto_now_add=True)

    class Meta:
        verbose_name = _("Dokument")
        verbose_name_plural = _("Dokumenti")

    def __str__(self):
        return f"{self.code} - {self.title}"

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, verbose_name=_("Dokument"), on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(_("Broj verzije"), max_length=20)  # npr. "v1"
    file = models.FileField(_("Fajl"), upload_to='documents/')
    issued_date = models.DateField(_("Datum izdavanja"))
    valid_until = models.DateField(_("Važi do"), null=True, blank=True)
    uploaded_by = models.ForeignKey('core.CustomUser', verbose_name=_("Postavio"), on_delete=models.SET_NULL, null=True)
    change_description = models.TextField(_("Opis promene"), blank=True)
    is_current = models.BooleanField(_("Trenutna verzija"), default=False)

    class Meta:
        ordering = ['-issued_date']
        verbose_name = _("Verzija dokumenta")
        verbose_name_plural = _("Verzije dokumenata")

    def __str__(self):
        return f"{self.document.code} - {self.version_number}"

class DocumentAccessLog(models.Model):
    user = models.ForeignKey('core.CustomUser', verbose_name=_("Korisnik"), on_delete=models.SET_NULL, null=True)
    document_version = models.ForeignKey(DocumentVersion, verbose_name=_("Verzija dokumenta"), on_delete=models.CASCADE)
    access_time = models.DateTimeField(_("Vreme pristupa"), auto_now_add=True)
    action = models.CharField(_("Akcija"), max_length=50, choices=[
        ('viewed', _('Pregledano')),
        ('downloaded', _('Preuzeto'))
    ])

    class Meta:
        verbose_name = _("Pristup dokumentu")
        verbose_name_plural = _("Pristupi dokumentima")

    def __str__(self):
        return f"{self.user} - {self.document_version} - {self.action}"
