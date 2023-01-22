from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from . import forms
from home.forms import SignUpForm, HospitalSignUpForm, AddDoctorForm, AddHospitalForm, AddScheduleForm, \
    AppointmentForm, UserUpdateForm, ProfileUpdateForm, CommentForm
from django.core.mail import send_mail
from home.models import Menu, Doctor, Rating, Hospital, Speciality, Schedule, Location, Appointment, Patient, Status, \
    Times, Comment
from django.urls import reverse


# from datetime import time


def index(request):
    current_user = request.user
    if not current_user.is_anonymous:
        if current_user.is_staff:
            if request.method == 'POST':
                hospital = Hospital.objects.get(user=current_user)
                hregisterform = HospitalSignUpForm(request.POST, request.FILES, instance=current_user)
                hform = AddHospitalForm(request.POST, request.FILES, instance=hospital)
                if hform.is_valid() and hregisterform.is_valid():
                    user = hregisterform.save()
                    user.save()
                    hospital = hform.save()
                    hospital.save()
                    login(request, user)
                    return redirect('home:home')
            else:
                hospital = Hospital.objects.get(user=current_user)
                hregisterform = HospitalSignUpForm(instance=current_user)
                hform = AddHospitalForm(instance=hospital)
                return render(request, 'hospital/hospitalhome.html', {'hform': hform, 'hregisterform': hregisterform})
        else:
            patient = Patient.objects.get(user=current_user)
            if not patient is None:
                context = {
                    'user': User.objects.get(username=current_user),
                    'hospitals': Hospital.objects.all(),
                    'doctors': Doctor.objects.all(),
                    'patient': patient
                }
                return render(request, 'home/userhome.html', context)
            else:
                context = {
                    'user': User.objects.get(username=current_user),
                    'hospitals': Hospital.objects.all(),
                    'doctors': Doctor.objects.all(),
                }
                return render(request, 'home/userhome.html', context)
    context = {
        'hospitals': Hospital.objects.all(),
        'doctors': Doctor.objects.all(),
    }
    return render(request, "home/index.html", context)


@login_required(login_url='/login')
def profile_edit(request):
    current_user = request.user
    if not current_user.is_anonymous and not current_user.is_staff:
        patient = Patient.objects.get(user=current_user)
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, instance=current_user)
            profile_form = ProfileUpdateForm(request.POST, instance=patient)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return redirect('/')
        else:
            user_form = UserUpdateForm(instance=current_user)
            profile_form = ProfileUpdateForm(instance=patient)
        return render(request, 'home/userprofile.html', {'user_form': user_form, 'profile_form': profile_form})
    return redirect('/')


def login_view(request):
    if request.method == 'POST':
        loginform = forms.LoginForm(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data.get("username")
            password = loginform.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        loginform = forms.LoginForm()
    return render(request, 'registration/login.html', {'loginform': loginform})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def getdoctors(request: HttpRequest) -> HttpResponse:
    current_user = request.user
    doctors = Doctor.objects.all()
    specialities = Speciality.objects.all()

    if not current_user.is_anonymous and not current_user.is_staff:
        for doctor in doctors:
            rating = Rating.objects.filter(doctor=doctor, user=current_user).first()
            doctor.user_rating = rating.rating if rating else 0
        return render(request, template_name='home/userdoctor.html', context={'doctors': doctors,
                                                                              'specialities': specialities,
                                                                              'current_user': current_user})
    return render(request, template_name='home/doctor.html',
                  context={'doctors': doctors, 'current_user': current_user})


def doctor_detail(request: HttpRequest, doctor_id: int) -> HttpResponse:
    current_user = request.user
    doctor = Doctor.objects.get(id=doctor_id)
    comments = Comment.objects.filter(doctor=doctor)
    if not current_user.is_anonymous and not current_user.is_staff:
        cform = CommentForm(doctor=doctor)
        check_appointment = Appointment.objects.filter(user=current_user, doctor=doctor, status=4)
        user_rating = Rating.objects.filter(user=current_user, doctor=doctor)
        user_comments = Comment.objects.filter(user=current_user)

        if user_comments.count() < check_appointment.count():
            commentable = True  # if completed appointments are more than the number of comments, the user can make comments.
        else:  # user can make a single comment for each of their completed appointments.
            commentable = False
        if check_appointment:
            can_vote = True
        else:
            can_vote = False
        if request.method == 'POST':
            cform = CommentForm(doctor, request.POST)
            if cform.is_valid():
                cmt = cform.save(commit=False)
                cmt.user = current_user
                cmt.doctor = doctor
                cmt.save()
                cform.save()
                return redirect('doctor_detail', doctor_id)
        return render(request, 'home/userdoctorsingle.html', {'doctor': doctor, 'can_vote': can_vote,
                                                              'check_appointment': check_appointment,
                                                              'user_rating': user_rating,
                                                              'cform': cform, 'comments': comments,
                                                              'user': current_user,
                                                              'user_comments': user_comments,
                                                              'commentable': commentable})
    return render(request, template_name='home/doctorsingle.html', context={'doctor': doctor, 'comments': comments})


def delete_comment(request, doctor_id: int, comment_id: int):
    # current_user = request.user
    doctor = Doctor.objects.get(id=doctor_id)
    comment = Comment.objects.get(id=comment_id)

    comment.delete()
    return HttpResponseRedirect(reverse('doctor_detail', args=[doctor_id], ))


def hospitals(request):
    current_user = request.user
    # url_parameter = request.GET.get("")
    context = Hospital.objects.all()
    if not current_user.is_anonymous and not current_user.is_staff:
        return render(request, 'home/userhospital.html', context={'hospitals': context})
    return render(request, 'home/hospital.html', context={'hospitals': context})


def hospital_detail(request: HttpRequest, hospital_id: int) -> HttpResponse:
    hospital = Hospital.objects.get(id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital)
    services = Speciality.objects.filter(doctor__in=doctors)
    current_user = request.user
    if not current_user.is_anonymous and not current_user.is_staff:
        return render(request, 'home/userhospitalsingle.html', context={'hospital': hospital, 'services': services})
    return render(request, 'home/hospitalsingle.html', context={'hospital': hospital, 'services': services})


def rate(request: HttpRequest, doctor_id: int, rating: int) -> HttpResponse:
    doctor = Doctor.objects.get(id=doctor_id)
    Rating.objects.filter(doctor=doctor, user=request.user).delete()
    doctor.rating_set.create(user=request.user, rating=rating)

    return getdoctors(request)


def contact(request):
    context = {
        'menus': Menu.objects.all(),
    }
    current_user = request.user

    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        # phone = request.POST['phone']
        subject = request.POST['subject']
        message = request.POST['message']

        send_mail(
            '[MediGo]Message from ' + name + ': ' + subject,
            message,
            email,
            # phone,
            ['']
        )
        if not current_user.is_anonymous and not current_user.is_staff:
            return render(request, 'home/usercontact.html', context)
        return render(request, 'home/contact.html', context)
    else:
        if not current_user.is_anonymous and not current_user.is_staff:
            return render(request, 'home/usercontact.html', context)
        return render(request, 'home/contact.html', context)


def register(request):
    if request.method == 'POST':
        registerform = SignUpForm(request.POST)
        if registerform.is_valid():
            user = registerform.save()
            user.refresh_from_db()
            patient = Patient.objects.create(user=user)
            patient.user = user
            patient.save()
            user.save()
            return redirect('home')
    else:
        registerform = SignUpForm()
    return render(request, 'registration/register.html', {'registerform': registerform})


def hospital_register(request):
    if request.method == 'POST':
        hregisterform = HospitalSignUpForm(request.POST, request.FILES)
        hform = AddHospitalForm(request.POST, request.FILES)
        if hregisterform.is_valid() and hform.is_valid():
            user = hregisterform.save()
            user.save()
            hospital = hform.save(commit=False)
            hospital.user = user
            hospital.save()

            return redirect('home')
    else:
        hregisterform = HospitalSignUpForm()
        hform = AddHospitalForm()
    return render(request, 'hospital/hospitalregister.html', {'hregisterform': hregisterform, 'hform': hform})


def about(request):
    return render(request, 'home/about.html')


@login_required(login_url='/login')
def add_doctor(request):
    current_user = request.user
    if current_user.is_staff:
        if not current_user.is_anonymous and request.method == 'POST':
            dform = AddDoctorForm(request.POST)
            if dform.is_valid():
                doctor = dform.save(commit=False)
                doctor.hospital = Hospital.objects.get(user=current_user)
                doctor.save()
            return redirect('home:home')
        else:
            dform = AddDoctorForm()
        return render(request, 'hospital/hadddoctor.html', {'dform': dform})
    else:
        return redirect('home')


# def add_hospital(request):
#     current_user = request.user
#     if not current_user.is_anonymous:
#         if request.method == 'POST':
#             hform = AddHospitalForm(request.POST)
#             if hform.is_valid():
#                 hospital = hform.save()
#                 new_hospital = Hospital.objects.create(hospital=hospital, user=current_user)
#                 return render(request, '', context={'new_hospital': new_hospital})
#         else:
#             hform = AddHospitalForm()
#         return render(request, 'hospital/add_hospital.html', {'hform': hform})
#     return redirect('')

@login_required(login_url='/login')
def view_doctors(request):
    current_user = request.user
    if not current_user.is_anonymous and current_user.is_staff:
        hospital = Hospital.objects.get(user=current_user)
        doctor = Doctor.objects.filter(hospital=hospital)
        return render(request, 'hospital/view_doctors.html', context={'doctors': doctor})
    return redirect('/')


@login_required(login_url='/login')
def doctor_delete(request, doctor_id: int):
    current_user = request.user
    if not current_user.is_staff or current_user.is_anonymous:
        return redirect('')
    else:
        doctor = Doctor.objects.get(id=doctor_id)
        doctor.delete()
        return HttpResponseRedirect(reverse('home:view_doctors'))


@login_required(login_url='/login')
def doctor_update(request, doctor_id: int):
    current_user = request.user
    if not current_user.is_staff or current_user.is_anonymous:
        return redirect('')
    else:
        if request.method == 'POST':
            doctor = Doctor.objects.get(id=doctor_id)
            dform = AddDoctorForm(request.POST, request.FILES, instance=doctor)
            if dform.is_valid():
                dform.save()
                return redirect('home:view_doctors')
        else:
            doctor = Doctor.objects.get(id=doctor_id)
            dform = AddDoctorForm(instance=doctor)
            return render(request, 'hospital/update_doctor.html', {'dform': dform})


# def deneme(request):
#
#     hregisterform = HospitalSignUpForm()
#     hform = AddHospitalForm()
#
#     return render(request, 'hospital/hospitalregister.html', {'hregisterform': hregisterform, 'hform': hform})

@login_required(login_url='/login')
def add_schedule(request):
    current_user = request.user

    if not current_user.is_anonymous and current_user.is_staff:
        hospital = Hospital.objects.get(user=current_user)
        doctors = Doctor.objects.filter(hospital=hospital)
        scform = AddScheduleForm(doctors=doctors)
        if request.method == 'POST':
            scform = AddScheduleForm(doctors, request.POST)
            if scform.is_valid():
                scform.save()
            return redirect('/')
        return render(request, 'hospital/add_schedule.html', {'scform': scform})
    return redirect('/')


@login_required(login_url='/login')
def view_schedule(request):
    current_user = request.user
    if not current_user.is_anonymous and current_user.is_staff:
        hospital = Hospital.objects.get(user=current_user)
        doctors = Doctor.objects.filter(hospital=hospital)
        schedules = Schedule.objects.filter(doctor__in=doctors)

        return render(request, 'hospital/view_schedule.html', {'schedules': schedules})
    else:
        return redirect('/')


@login_required(login_url='/login')
def delete_schedule(request, schedule_id: int):
    current_user = request.user
    if not current_user.is_staff and current_user.is_anonymous:
        return redirect('')
    else:
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.delete()
        return HttpResponseRedirect(reverse('home:view_schedule'))


def view_appointments(request):
    current_user = request.user
    if not current_user.is_anonymous and current_user.is_staff:
        hospital = Hospital.objects.get(user=current_user)
        appointment = Appointment.objects.filter(hospital=hospital)
        return render(request, 'hospital/hospitalappointments.html', {'appointments': appointment})
    return redirect('/')


@login_required(login_url='/login')
def appointment(request):
    current_user = request.user
    if not current_user.is_anonymous and not current_user.is_staff:
        aform = AppointmentForm()
        if request.method == 'POST':
            aform = AppointmentForm(request.POST)
            if aform.is_valid():
                user = aform.save(commit=False)
                user.user = current_user
                user.save()
                status = aform.save(commit=False)
                status.status = Status.objects.get(name='Aktif')
                status.save()
                aform.save()
                return redirect('home:appointments')
        return render(request, 'home/appointment.html', {'aform': aform})
    return redirect('/')


@login_required(login_url='/login')
def appointment_load_locations(request):
    spec_id = request.GET.get('field')
    q1 = Doctor.objects.filter(speciality=spec_id)
    q2 = Hospital.objects.filter(doctor__in=q1)
    locations = Location.objects.filter(hospital__in=q2).order_by('name').distinct()
    return render(request, 'home/location_list.html', {'locations': locations})


@login_required(login_url='/login')
def appointment_load_hospitals(request):
    spec_id = request.GET.get('field')
    location_id = request.GET.get('location')
    q1 = Doctor.objects.filter(speciality=spec_id)
    q2 = Hospital.objects.filter(doctor__in=q1)
    q3 = Location.objects.filter(hospital__in=q2).order_by('name')
    q4 = q2.filter(location__in=q3)
    hospitals = q4.filter(location=location_id).distinct()
    return render(request, 'home/hospital_list.html', {'hospitals': hospitals})


@login_required(login_url='/login')
def appointment_load_doctors(request):
    spec_id = request.GET.get('field')
    location_id = request.GET.get('location')
    hospital_id = request.GET.get('hospital')
    q1 = Doctor.objects.filter(speciality=spec_id)
    q2 = Hospital.objects.filter(doctor__in=q1)
    q3 = Location.objects.filter(hospital__in=q2).order_by('name')
    q4 = q2.filter(location__in=q3)
    q5 = q4.filter(location=location_id).distinct()
    q6 = Doctor.objects.filter(speciality=spec_id, hospital__in=q5, hospital__location_id=location_id).distinct()
    doctors = q6.filter(hospital=hospital_id).distinct()
    return render(request, 'home/doctor_list.html', {'doctors': doctors})


@login_required(login_url='/login')
def appointment_load_dates(request):
    doctor_id = request.GET.get('doctor')
    dates = Schedule.objects.filter(doctor=doctor_id)
    return render(request, 'home/date_list.html', {'dates': dates})


@login_required(login_url='/login')
def appointment_load_times(request):
    doctor_id = request.GET.get('doctor')
    date_id = request.GET.get('date')
    schedule = Schedule.objects.get(doctor=doctor_id, id=date_id)
    print(schedule)
    exclude = Appointment.objects.filter(doctor=doctor_id, date=date_id, status__name='Aktif').values_list('time',
                                                                                                           flat=True)
    times = Times.objects.exclude(id__in=exclude)
    leaving_time = schedule.last_hour.time

    if schedule.time_interval == Schedule.Half:
        times = [time for time in times if time.time.minute in (0, 30)]
    else:
        pass

    if schedule.time_interval == Schedule.Exact:
        times = [time for time in times if time.time.minute == 0]
    else:
        pass

    if schedule.last_hour:
        times = [time for time in times if time.time < leaving_time]
    else:
        pass

    return render(request, 'home/time_list.html', {'times': times})


@login_required(login_url='/login')
def user_appointments(request):
    current_user = request.user
    if not current_user.is_anonymous and not current_user.is_staff:
        appointment = Appointment.objects.filter(user=current_user)
        return render(request, 'home/userappointments.html', {'appointments': appointment})
    return redirect('/')


@login_required(login_url='/login')
def appointment_cancel(request, appointment_id: int):
    current_user = request.user
    appointment = Appointment.objects.get(id=appointment_id)
    if not current_user.is_staff and not current_user.is_anonymous and not appointment.status.id == 4:
        appointment.status = Status.objects.get(id=3)
        appointment.save()
        return HttpResponseRedirect(reverse('home:appointments'))
    return redirect('/')


@login_required(login_url='/login')
def appointment_done(request, appointment_id: int):
    current_user = request.user
    appointment = Appointment.objects.get(id=appointment_id)
    if current_user.is_staff and not current_user.is_anonymous and not appointment.status.id == 3:
        appointment.status = Status.objects.get(id=4)
        appointment.save()
        return HttpResponseRedirect(reverse('home:view_appointments'))
    return redirect('/')
