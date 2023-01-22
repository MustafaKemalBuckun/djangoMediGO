from ckeditor.fields import RichTextField
from django import forms
# from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# import datetime as dt

from django.forms import ModelChoiceField

from home.models import Doctor, Hospital, Schedule, Comment, Appointment, Location, Patient, Times

# Create your forms here.


class SignUpForm(UserCreationForm):
    username = forms.CharField(required=True, max_length=15)
    first_name = forms.CharField(required=True, max_length=15)
    last_name = forms.CharField(required=True, max_length=15)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=15)
    password = forms.CharField(max_length=60, widget=forms.PasswordInput)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ('user',)


class HospitalSignUpForm(UserCreationForm):
    username = forms.CharField(required=True, max_length=30)
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(HospitalSignUpForm, self).save()
        user.is_staff = True
        if commit:
            user.save()
        return user


class AddDoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = ('hospital',)


class AddHospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        exclude = ('user',)


class DateInput(forms.DateInput):
    input_type = 'date'


class AddScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['doctor', 'days', 'time_interval', 'last_hour']
        widgets = {
            'days': DateInput()
        }

    def __init__(self, doctors, *args, **kwargs):
        super(AddScheduleForm, self).__init__(*args, **kwargs)
        self.fields['doctor'] = ModelChoiceField(queryset=doctors)
        self.fields['days'].widget.attrs.update({'min': '2023-01-12', 'max': '2023-03-01'})


class DeleteScheduleForm(forms.Form):
    doctor = forms.ModelChoiceField(queryset=Schedule.objects.filter(), required=True)
    days = forms.ModelChoiceField(queryset=Schedule.objects.values_list('days', flat=True), required=True)

    def __init__(self, doctors, *args, **kwargs):
        super(DeleteScheduleForm, self).__init__(*args, **kwargs)
        self.fields['doctor'] = ModelChoiceField(queryset=doctors)
        self.fields['days'] = ModelChoiceField(queryset=Schedule.objects.none())


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ('sent_date',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['field'].queryset = Speciality.objects.all()
        self.fields['location'].queryset = Location.objects.none()
        self.fields['hospital'].queryset = Hospital.objects.none()
        self.fields['doctor'].queryset = Doctor.objects.none()
        self.fields['date'].queryset = Schedule.objects.none()
        # self.fields['status'].queryset = Status.objects.filter(name='Inaktif')
        self.fields['status'].required = False
        self.fields['time'].queryset = Times.objects.none()
        # self.fields['user'].queryset = User.objects.none()
        # self.fields['status'].queryset =

    def is_valid(self):
        self.fields['location'].queryset = Location.objects.all()
        self.fields['hospital'].queryset = Hospital.objects.all()
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['date'].queryset = Schedule.objects.all()
        self.fields['time'].queryset = Times.objects.all()
        # self.fields['user'] =
        return super(AppointmentForm, self).is_valid()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('sent_date',)

    def __init__(self, doctor, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        # self.fields['doctor'] = ModelChoiceField(queryset=Doctor.objects.filter(id=doctor.id))
        self.fields['doctor'].required = False

    def is_valid(self):
        return super(CommentForm, self).is_valid()
