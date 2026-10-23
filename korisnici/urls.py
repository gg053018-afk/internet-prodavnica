from django.urls import path
from . import views

urlpatterns = [
    path('registracija/', views.registracija, name='registracija'),
    path('prijava/', views.prijava, name='prijava'),
    path('odjava/', views.odjava, name='odjava'),
    path('aktivacija/<uidb64>/<token>/', views.aktivacija, name='aktivacija'),
    path('demo-aktivacija/', views.demo_aktivacija, name='demo_aktivacija'),
]