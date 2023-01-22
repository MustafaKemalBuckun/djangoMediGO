from ckeditor.fields import RichTextField
# from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.core.validators import FileExtensionValidator, RegexValidator
from django.core.validators import validate_comma_separated_integer_list
from django.db.models import Avg
from django.utils import timezone

# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=30, blank=False)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=20, blank=False, default=None)

    def __str__(self):
        return self.name


class Times(models.Model):
    time = models.TimeField(default=None, blank=True)

    def __str__(self):
        return str(self.time)


class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=50)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    info = models.CharField(max_length=60, default=None, blank=True)
    about = RichTextField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False)
    staff_count = models.IntegerField(default=0)
    # foundation_date = models.IntegerField(default=0)
    # bed_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def average_rating(self) -> float:
        return Rating.objects.filter(hospital=self).aggregate(Avg("rating"))["rating__avg"] or 0


class Speciality(models.Model):
    parent_id = models.BigIntegerField(default=0)
    name = models.CharField(max_length=40)
    sub_branch = models.BooleanField(default=False)
    parent_path = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list], default=0)

    def __str__(self):
        return self.name


class Doctor(models.Model):

    name = models.CharField(max_length=40)
    image = models.ImageField(blank=True, upload_to='images/')
    description = models.CharField(max_length=80)
    # speciality = MultiSelectField(choices=Specialities.choices)
    # language = models.Languages
    biography = RichTextField(blank=True)
    video = models.FileField(blank=True, upload_to='videos')
    validator = [FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, default=None, blank=False)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, default=None, blank=False)

    def __str__(self):
        return self.name

    def average_rating(self) -> float:
        return Rating.objects.filter(doctor=self).aggregate(Avg("rating"))["rating__avg"] or 0


class Schedule(models.Model):

    All = 'Tüm saatler'
    Half = '30 Dakikada Bir'
    Exact = 'Saatte Bir'
    CHOICES = ((All, 'Tüm saatler'), (Half, '30 Dakikada Bir'), (Exact, 'Saatte Bir'))
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=False)
    days = models.DateField(default=timezone.now, blank=True, null=True)
    time_interval = models.CharField(choices=CHOICES, default=None, blank=True, max_length=20)
    last_hour = models.ForeignKey(Times, on_delete=models.CASCADE, default=None, blank=False)
    # shift = models.BooleanField(default=False)      # False = tam gün çalışma, True = Yarım gün çalışma

    class Meta:
        unique_together = ["doctor", "days"]


class Appointment(models.Model):

    field = models.ForeignKey(Speciality, on_delete=models.RESTRICT, blank=False, default=None)
    location = models.ForeignKey(Location, on_delete=models.RESTRICT, blank=False, default=None)
    hospital = models.ForeignKey(Hospital, on_delete=models.RESTRICT, blank=False, default=None)
    doctor = models.ForeignKey(Doctor, on_delete=models.RESTRICT, blank=False, default=None)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, default=None)
    date = models.ForeignKey(Schedule, on_delete=models.RESTRICT, blank=False, default=None)
    time = models.ForeignKey(Times, on_delete=models.RESTRICT, blank=False, default=timezone.now)
    sent_date = models.DateField(auto_now_add=True)
    status = models.ForeignKey(Status, default=None, on_delete=models.RESTRICT, max_length=10, null=True)
    # is_active = models.BooleanField(blank=False, default=False)
    class Meta:
        ordering = ['-sent_date']


class Rating(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, default=None, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=None, blank=False)
    rating = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return f"{self.doctor.name}: {self.rating}"


class Menu(models.Model):

    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Yalnızca alfanumerik karakterler kabul edilir.')

    title = models.CharField(max_length=15, unique=True, validators=[alphanumeric])
    url = models.CharField(max_length=15, unique=True, validators=[alphanumeric])
    display = models.BooleanField()

    def __str__(self):
        return self.title


class Patient(models.Model):
    Male = 'Erkek'
    Female = 'Kadın'
    NotSpecified = 'Belirtilmedi'
    Gender_Choices = [(Male, 'Erkek'), (Female, 'Kadın'), (NotSpecified, 'Belirtilmedi')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
    weight = models.IntegerField(default=0, blank=True)
    height = models.IntegerField(default=0, blank=True)
    age = models.IntegerField(default=0, blank=True)
    gender = models.CharField(max_length=15, choices=Gender_Choices, default=NotSpecified, blank=True)


class Comment(models.Model):

    title = models.CharField(max_length=30)
    comment_detail = RichTextField(blank=False, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=None, blank=True)
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True)
    sent_date = models.DateTimeField(auto_now_add=True)
    # rating = models.IntegerField(choices=CHOICES, default=None, blank=True)
    class Meta:
        ordering = ['-sent_date']
        unique_together = ['title', 'comment_detail']


# class Day(models.Model):
#     DAY_CHOICES = (
#         ("pazartesi", "Pazartesi"),
#         ("salı", "Salı"),
#         ("çarşamba", "Çarşamba"),
#         ("perşembe", "Perşembe"),
#         ("cuma", "Cuma"),
#         ("cumartesi", "Cumartesi"),
#     )
#
#     name = models.CharField(max_length=10, choices=DAY_CHOICES, blank=False, default="Pazartesi")
#
#     def __str__(self):
#         return self.name
    # day = models.ManyToManyField(Day)
    # timeblock = models.TimeField(default=timezone.now)
