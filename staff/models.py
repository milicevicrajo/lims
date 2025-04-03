from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Laboratory
from methods.models import Method
from django.dispatch import receiver
from django.db.models.signals import post_save

class Staff(models.Model):
    first_name = models.CharField(_("Ime"), max_length=255)
    last_name = models.CharField(_("Prezime"), max_length=255)
    date_of_birth = models.DateField(_("Datum rođenja"), null=True, blank=True)
    place = models.CharField(_("Mesto"), max_length=255)
    jmbg = models.CharField(_("JMBG"), max_length=13, unique=True)
    education_level = models.CharField(_("Stepen obrazovanja"), max_length=255)
    school = models.CharField(_("Škola"), max_length=255)
    academic_title = models.CharField(_("Akademska titula"), max_length=255)
    scientific_title = models.CharField(_("Naučno zvanje"), max_length=255)
    laboratory = models.ForeignKey('core.Laboratory', on_delete=models.SET_NULL, verbose_name=_("Organizaciona celina"),null=True, blank=True)
    start_date_in_profession = models.DateField(_("Početak rada u struci"), null=True, blank=True)
    start_date_in_ims = models.DateField(_("Početak rada u IMS"), null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class JobPosition(models.Model):
    JOB_TYPE_CHOICES = [
        ('research', _("Istraživačka radna mesta")),
        ('technical', _("Radna mesta za obavljanje stručnih tehničkih poslova")),
    ]

    title = models.CharField(_("Naziv radnog mesta"), max_length=255)
    code = models.CharField(_("Broj radnog mesta"), max_length=20)
    job_type = models.CharField(_("Tip radnog mesta"), max_length=50, choices=JOB_TYPE_CHOICES)
    subcategory = models.CharField(_("Podkategorija"), max_length=255, blank=True)

    process_description = models.TextField(_("Opis radnog procesa"), blank=True, help_text="Odvojite tačke novim redom")

    def get_process_description_as_list(self):
        """Convert the process description into a list of bullet points."""
        if self.process_description:
            return [point.strip() for point in self.process_description.splitlines() if point.strip()]
        return []

    def __str__(self):
        return self.title

class StaffJobPosition(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, verbose_name=_("Radno mesto"))
    start_date = models.DateField(_("Datum početka"), null=False)
    end_date = models.DateField(_("Datum završetka"), null=True, blank=True)

    class Meta:
        verbose_name = _("Radno mesto zaposlenog")
        verbose_name_plural = _("Radna mesta zaposlenih")

    def __str__(self):
        return f"{self.staff} - {self.job_position}"

    @property
    def is_active(self):
        """Check if the position is active (no end date)."""
        return self.end_date is None
    

class ProfessionalExperience(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    experience = models.TextField(_("Stručno iskustvo"), blank=True)

    def __str__(self):
        return f"({self.staff} - {self.experience})"

class TrainingCourse(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    training_course = models.TextField(_("Obuke/Usavršavanja"), blank=True)

    def __str__(self):
        return f"{self.training_course} ({self.staff})"

class MembershipInInternationalOrg(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    organization_name = models.CharField(_("Naziv organizacije"), max_length=255)

    def __str__(self):
        return f"{self.organization_name} ({self.staff})"

class Training(models.Model):
    TRAINING_TYPE_CHOICES = [
        ('Obuka za obavljanje radnih zadataka', 'Obuka za obavljanje radnih zadataka'),
        ('Stručno usavršavanje', 'Stručno usavršavanje'),
        ('Obuka za sistem menadžmenta', 'Obuka za sistem menadžmenta'),
        ('Specijalistička obuka', 'Specijalistička obuka'),
    ]
    laboratory = models.ForeignKey('core.Laboratory', verbose_name=_("Laboratorija"), on_delete=models.SET_NULL, null=True)
    training_type = models.CharField(_("Vrsta obuke"), max_length=50, choices=TRAINING_TYPE_CHOICES, default='Laboratorija')
    training_name = models.TextField(_("Naziv obuke"), max_length=250, help_text="Odvojite tačke novim redom")
    location = models.CharField(_("Mesto održavanja obuke"), max_length=255)
    start_date = models.DateField(_("Datum početka obuke"))
    end_date = models.DateField(_("Datum završetka obuke"))
    instructors = models.ManyToManyField('Staff', verbose_name=_("Nosilac obuke - Zaposleni"), related_name='instructed_trainings', blank=True)
    instructors_other = models.TextField(verbose_name=_("Nosilac obuke - Ostali"), blank=True, null=True)
    training_material = models.TextField(_("Materijal za obuku"), blank=True, null=True)
    staff = models.ManyToManyField('Staff', verbose_name=_("Zaposleni"), related_name='attended_trainings')
    methods = models.ManyToManyField('methods.Method', verbose_name=_("Metode"), blank=True)
    document = models.CharField(_("Naziv dokumenta koji potvrđuje uspešnost obuke"), max_length=255, blank=True, null=True)
    training_effectiveness = models.TextField(_("Vrednovanje efektivnosti obuke"), blank=True, null=True)
    report = models.FileField(_("Izveštaj sa obuke"), upload_to='staff/trainings/', max_length=100, blank=True, null=True)
    report_date = models.DateField(_("Datum izveštaja"), null=True, blank=True)
    r_b_z = models.CharField(_("R.b.z."), max_length=255, blank=True, null=True)
    report_submitted = models.ForeignKey('Staff', verbose_name=_("Izveštaj podneo"), on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_reports')
    
    def get_training_name_as_list(self):
        """Convert the process description into a list of bullet points."""
        if self.training_name:
            return [point.strip() for point in self.training_name.splitlines() if point.strip()]
        return []
    
    def get_training_material_as_list(self):
        """Convert the process description into a list of bullet points."""
        if self.training_material:
            return [point.strip() for point in self.training_material.splitlines() if point.strip()]
        return []
    
    def __str__(self):
        return f"Obuka {self.training_name} od {self.start_date}"

class TrainingTests(models.Model):
    staff = models.ForeignKey('Staff', verbose_name=_("Zaposleni"), on_delete=models.CASCADE, blank=True)
    method = models.ForeignKey('methods.Method', verbose_name=_("Metoda"), on_delete=models.CASCADE, blank=True)
    test = models.FileField(_("Test (PDF)"), upload_to='staff/staff_test_results/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.staff} - {self.training}"

class StaffMethodTraining(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    method = models.ForeignKey(Method, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('staff', 'method', 'training')

@receiver(post_save, sender=Training)
def create_staff_method_training(sender, instance, **kwargs):
    methods = instance.methods.all()
    staff_members = instance.staff.all()

    if methods.exists() and staff_members.exists():
        for staff in staff_members:
            for method in methods:
                StaffMethodTraining.objects.get_or_create(
                    staff=staff, method=method, training=instance
                )

class AuthorizationType(models.Model):
    name = models.CharField(_("Naziv ovlašćenja"), max_length=255)
    description = models.TextField(_("Opis"), blank=True, null=True)

    def __str__(self):
        return self.name

class Authorization(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    method = models.ForeignKey('methods.Method', on_delete=models.CASCADE, verbose_name=_("Metoda"))
    authorization_type = models.ForeignKey('AuthorizationType', on_delete=models.CASCADE, verbose_name=_("Ovlašćenje"))
    date = models.DateField(_("Datum dodele ovlašćenja"))
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['staff', 'method', 'authorization_type'], name='unique_authorization')
        ]

    def __str__(self):
        return f"{self.staff} - {self.method} - {self.authorization_type}"
    
class NoMethodAuthorization(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, verbose_name=_("Zaposleni"))
    authorization = models.CharField(_("Naziv ovlašćenja"), max_length=255)
    date = models.DateField(_("Datum dodele ovlašćenja"))
    
    def __str__(self):
        return f"{self.staff} - {self.authorization}"