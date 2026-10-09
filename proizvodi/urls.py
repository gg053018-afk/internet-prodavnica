from django.urls import path
from . import views

urlpatterns = [
    path('', views.pocetna, name='pocetna'),
    path('proizvod/<int:proizvod_id>/', views.detalji_proizvoda, name='detalji_proizvoda'),
    path('korpa/', views.korpa, name='korpa'),
    path('narudzba/', views.narudzba, name='narudzba'),
    path('moje-narudzbe/', views.moje_narudzbe, name='moje_narudzbe'),
]