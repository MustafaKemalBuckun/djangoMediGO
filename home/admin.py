from django.contrib import admin
from django.db import models
from django.forms import DateInput

# from .forms import ScheduleAdminForm
from .models import Menu, Doctor, Speciality, Hospital, Patient, Rating, Location, Schedule, Appointment, \
    Status, Times


class FilterPosts(admin.ModelAdmin):
    list_display = ("title", "date", "author", "category")
    list_filter = ("author", "category")


class AdminDoctorDisplay(admin.ModelAdmin):
    list_display = ['name', 'description', 'hospital', 'speciality']
    list_filter = ['name', 'description', 'hospital', 'speciality']


class AdminHospitalDisplay(admin.ModelAdmin):
    list_display = ['title', 'location', 'staff_count', 'location']
    list_filter = ['title', 'location', 'staff_count', 'location']


class AdminPatientDisplay(admin.ModelAdmin):
    list_display = ['user', 'weight', 'height', 'age', 'gender']
    list_filter = ['user', 'weight', 'height', 'age', 'gender']


class AdminScheduleDisplay(admin.ModelAdmin):
    list_display = ['doctor', 'days']
    list_filter = ['doctor', 'days']


admin.site.register(Speciality)
admin.site.register(Doctor, AdminDoctorDisplay)
admin.site.register(Hospital, AdminHospitalDisplay)
admin.site.register(Menu)
admin.site.register(Rating)
admin.site.register(Location)
admin.site.register(Appointment)
admin.site.register(Status)
admin.site.register(Times)
# admin.site.register(Day)
# admin.site.register(Schedule)
admin.site.register(Patient, AdminPatientDisplay)
admin.site.register(Schedule, AdminScheduleDisplay)

