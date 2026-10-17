from django.test import TestCase
from django.contrib.auth.models import User
from .models import Narudzba

# Create your tests here.
class TestPocetneStranice(TestCase):
    def test_pocetna_stranica(self):
        odgovor = self.client.get("/")
        self.assertEqual(odgovor.status_code, 200)

    def test_stranica_prijave(self):
        odgovor = self.client.get("/prijava/")
        self.assertEqual(odgovor.status_code, 200)

    def test_stranica_registracije(self):
        odgovor = self.client.get("/registracija/")
        self.assertEqual(odgovor.status_code, 200)

    def test_moje_narudzbe_bez_prijave(self):
        odgovor = self.client.get("/moje-narudzbe/")
        self.assertRedirects(odgovor, "/prijava/?next=/moje-narudzbe/")

    def test_detalji_narudzbe_bez_prijave(self):
        odgovor = self.client.get("/moje-narudzbe/1/")
        self.assertRedirects(odgovor, "/prijava/?next=/moje-narudzbe/1/")

    def test_zastita_tudje_narudzbe(self):
        korisnik1 = User.objects.create_user(
            username="korisnik1",
            password="test12345"
        )

        korisnik2 = User.objects.create_user(
            username="korisnik2",
            password="test12345"
        )

        self.client.force_login(korisnik2)

        narudzba = Narudzba.objects.create(
            korisnik=korisnik1,
            ime="Marko",
            prezime="Markovic",
            adresa="Test adresa 1",
            grad="Banja Luka",
            postanski_broj="78000",
            telefon="060123456",
            email="marko@example.com"
        )

        odgovor = self.client.get(f"/moje-narudzbe/{narudzba.id}/")
        self.assertEqual(odgovor.status_code, 404)

    def test_pristup_vlastitoj_narudzbi(self):
        korisnik = User.objects.create_user(
            username="testkorisnik",
            password="test12345"
        )
        self.client.force_login(korisnik)

        narudzba = Narudzba.objects.create(
            korisnik=korisnik,
            ime="Marko",
            prezime="Markovic",
            adresa="Test adresa 1",
            grad="Banja Luka",
            postanski_broj="78000",
            telefon="060123456",
            email="marko@example.com"
        )
        odgovor = self.client.get(f"/moje-narudzbe/{narudzba.id}/")
        self.assertEqual(odgovor.status_code, 200)
