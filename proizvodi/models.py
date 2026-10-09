from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Proizvod(models.Model):
    naziv = models.CharField(max_length=200)
    kolicina = models.PositiveIntegerField()
    cijena = models.DecimalField(max_digits=10, decimal_places=2)
    opis = models.TextField()
    slika = models.ImageField(upload_to='proizvodi/')
    kategorija = models.CharField(max_length=100)
    dostupan = models.BooleanField(default=True)
    rok_trajanja = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.naziv

class Narudzba(models.Model):
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE,
        null=True, blank=True)
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    adresa = models.CharField(max_length=200)
    grad = models.CharField(max_length=100)
    postanski_broj = models.CharField(max_length=20)
    telefon = models.CharField(max_length=30)
    email = models.EmailField()

    ukupno = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    datum_narudzbe = models.DateTimeField(auto_now_add=True, null=True)

    STATUS_CHOICES = [
        ("Na čekanju", "Na čekanju"),
        ("Poslato", "Poslato"),
        ("Isporučeno", "Isporučeno"),
    ]

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Na čekanju"
    )

    def __str__(self):
        return self.ime + " " + self.prezime

class StavkaNarudzbe(models.Model):
    narudzba = models.ForeignKey(Narudzba, on_delete=models.CASCADE)
    proizvod = models.ForeignKey(Proizvod, on_delete=models.CASCADE)
    kolicina = models.PositiveIntegerField()
    cijena = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.proizvod.naziv