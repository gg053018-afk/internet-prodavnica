from django.contrib import admin

from .models import Proizvod, Narudzba, StavkaNarudzbe

# Register your models here.

@admin.register(Proizvod)
class ProizvodAdmin(admin.ModelAdmin):
    list_display = ("id", "naziv", "cijena", "kolicina", "dostupan")
    search_fields = ("naziv",)
    list_filter = ("dostupan",)

@admin.register(Narudzba)
class NarudzbaAdmin(admin.ModelAdmin):
    list_display = ("id", "ime", "prezime", "datum_narudzbe", "ukupno", "status")
    list_filter = ("status",)
    search_fields = ("ime", "prezime", "email", "=id")
    ordering = ("-id",)

admin.site.register(StavkaNarudzbe)