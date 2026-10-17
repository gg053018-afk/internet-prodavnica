from django.test import TestCase
from django.contrib.auth.models import User
from .models import Narudzba, Proizvod

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

    def test_kreiranje_proizvoda(self):

        proizvod = Proizvod.objects.create(
            naziv="Mlijeko",
            kolicina=10,
            cijena=2.50,
            opis="Svjeze mlijeko",
            slika="proizvodi/mlijeko.jpg",
            kategorija="Mliječni proizvodi"
        )

        self.assertEqual(proizvod.naziv, "Mlijeko")
        self.assertEqual(proizvod.kolicina, 10)
        self.assertEqual(proizvod.cijena, 2.50)
        self.assertEqual(proizvod.kategorija, "Mliječni proizvodi")
        self.assertTrue(proizvod.dostupan)
        self.assertEqual(proizvod.opis, "Svjeze mlijeko")
        self.assertEqual(Proizvod.objects.count(), 1)

    def test_nedostupan_proizvod(self):
        proizvod = Proizvod.objects.create(
            naziv="Jogurt",
            kolicina=0,
            cijena=1.80,
            opis="Vocni jogurt",
            slika="proizvodi/jogurt.jpg",
            kategorija="Mliječni proizvodi",
            dostupan=False
        )

        self.assertFalse(proizvod.dostupan)

    def test_dodavanje_proizvoda_u_korpu(self):
        proizvod = Proizvod.objects.create(
            naziv="Hljeb",
            kolicina=20,
            cijena=2.00,
            opis="Bijeli hljeb",
            slika="proizvodi/hljeb.jpg",
            kategorija="Pekarski proizvodi"
        )

        odgovor = self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "3"
        })

        self.assertEqual(self.client.session["korpa"][str(proizvod.id)], 3)

    def test_uklanjanje_proizvoda_iz_korpe(self):
        proizvod = Proizvod.objects.create(
            naziv="Sok",
            kolicina=15,
            cijena=3.00,
            opis="Sok od narandze",
            slika="proizvodi/sok.jpg",
            kategorija="Pica"
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "2"
        })

        self.client.post("/korpa/", {
            "akcija": "ukloni",
            "proizvod_id": proizvod.id
        })

        self.assertNotIn(str(proizvod.id), self.client.session["korpa"])

    def test_prevelika_kolicina_u_korpi(self):
        proizvod = Proizvod.objects.create(
            naziv="Hljeb",
            kolicina=5,
            cijena=2.00,
            opis="Bijeli hljeb",
            slika="proizvodi/hljeb.jpg",
            kategorija="Pekarski proizvodi"
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "10"
        })