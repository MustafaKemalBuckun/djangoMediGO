"""djangoWebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('', include(('home.urls', 'home'), namespace='home')),
    path('contact/', views.contact),
    path('doctors/', views.getdoctors),
    path('hospitals/', views.hospitals),
    path('hospitals/<int:hospital_id>', views.hospitals),
    path('rate/<int:doctor_id>/<int:rating>/', views.rate),
    # path('blog/', views.posts),
    path('about/', views.about),
    path('userhome/', views.index),
    # path('hospitalhome/', views.index),
    path('doctors/', views.getdoctors),
    path('doctors/<int:id>', views.doctor_detail),
    # path('services/', views.services),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('hlogin/', views.hlogin),
    path('hregister/', views.hospital_register),
    # path('deneme/', views.deneme),
    path('captcha/', include('captcha.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
