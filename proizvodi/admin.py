from django.contrib import admin

from .models import Proizvod, Narudzba, StavkaNarudzbe

class StavkaNarudzbeInline(admin.TabularInline):
    model = StavkaNarudzbe
    extra = 0
    fields = ("proizvod", "kolicina", "cijena", "ukupna_cijena")
    readonly_fields = ("ukupna_cijena",)

    def ukupna_cijena(self, obj):
        if obj.pk:
            return obj.kolicina * obj.cijena
        return 0

    ukupna_cijena.short_description = "Ukupna cijena (KM)"

# Register your models here.

@admin.register(Proizvod)
class ProizvodAdmin(admin.ModelAdmin):
    list_display = ("id", "naziv", "cijena", "kolicina", "dostupan")
    search_fields = ("naziv",)
    list_filter = ("dostupan",)

@admin.register(Narudzba)
class NarudzbaAdmin(admin.ModelAdmin):
    inlines = [StavkaNarudzbeInline]
    list_display = ("id", "ime", "prezime", "datum_narudzbe", "ukupno", "status")
    list_filter = ("status",)
    search_fields = ("ime", "prezime", "email", "telefon", "=id")
    ordering = ("-id",)

@admin.register(StavkaNarudzbe)
class StavkaNarudzbeAdmin(admin.ModelAdmin):
    list_display = ("id", "narudzba", "proizvod", "kolicina", "cijena", "ukupna_cijena")
    readonly_fields = ("ukupna_cijena",)
    
    def ukupna_cijena(self, obj):
        return obj.kolicina * obj.cijena

    ukupna_cijena.short_description = "Ukupna cijena (KM)"