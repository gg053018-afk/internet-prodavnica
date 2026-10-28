from django.test import TestCase
from django.contrib.auth.models import User
from .models import Narudzba, Proizvod, StavkaNarudzbe

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

        self.assertNotIn(str(proizvod.id), self.client.session.get("korpa", {}))

    def test_narudzba_prazna_korpa(self):
        korisnik = User.objects.create_user(
            username="kupac_test",
            password="test12345"
        )

        self.client.force_login(korisnik)
        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertContains(odgovor, "Korpa je prazna.")

    def test_narudzba_bez_obaveznih_podataka(self):
        korisnik = User.objects.create_user(
            username="kupac_bez_prezimena",
            password="test12345"
        )

        self.client.force_login(korisnik)
        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertContains(odgovor, "Morate popuniti sva obavezna polja.")

    def test_uspjesna_narudzba(self):
        korisnik = User.objects.create_user(
            username="kupac_uspjesna_narudzba",
            password="test12345"
        )

        self.client.force_login(korisnik)

        proizvod = Proizvod.objects.create(
            naziv="Hljeb",
            kolicina=10,
            cijena=2.50,
            opis="Bijeli hljeb",
            slika="proizvodi/test_hljeb.jpg",
            kategorija="Pekarski proizvodi",
            dostupan=True
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "2"
        })

        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertEqual(Narudzba.objects.count(), 1)
        proizvod.refresh_from_db()
        self.assertEqual(proizvod.kolicina, 8)

        narudzba = Narudzba.objects.first()
        self.assertEqual(narudzba.ukupno, 5)
        self.assertEqual(self.client.session.get("korpa"), {})
        self.assertEqual(StavkaNarudzbe.objects.count(), 1)

        stavka = StavkaNarudzbe.objects.first()
        self.assertEqual(stavka.kolicina, 2)
        self.assertEqual(stavka.proizvod, proizvod)
        self.assertEqual(stavka.cijena, 2.50)
        self.assertEqual(narudzba.korisnik, korisnik)
        self.assertEqual(narudzba.status, "Na čekanju")
        self.assertEqual(stavka.narudzba, narudzba)

    def test_narudzba_nedovoljno_zaliha(self):
        korisnik = User.objects.create_user(
            username="kupac_nedovoljno_zaliha",
            password="test12345"
        )

        self.client.force_login(korisnik)

        proizvod = Proizvod.objects.create(
            naziv="Mlijeko",
            kolicina=2,
            cijena=3.00,
            opis="Svježe mlijeko",
            slika="proizvodi/test_mlijeko.jpg",
            kategorija="Mliječni proizvodi",
            dostupan=True
        )

        sesija = self.client.session
        sesija["korpa"] = {str(proizvod.id): 5}
        sesija.save()

        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertContains(odgovor, "Nema dovoljno proizvoda na stanju.")
        self.assertEqual(Narudzba.objects.count(), 0)

        proizvod.refresh_from_db()
        self.assertEqual(proizvod.kolicina, 2)
        self.assertEqual(StavkaNarudzbe.objects.count(), 0)

    def test_proizvod_nedostupan_nakon_kupovine(self):
        korisnik = User.objects.create_user(
            username="kupac_posljednji_proizvod",
            password="test12345"
        )

        self.client.force_login(korisnik)

        proizvod = Proizvod.objects.create(
            naziv="Jogurt",
            kolicina=1,
            cijena=2.00,
            opis="Svježi jogurt",
            slika="proizvodi/test_jogurt.jpg",
            kategorija="Mliječni proizvodi",
            dostupan=True
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "1"
        })

        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        proizvod.refresh_from_db()

        self.assertEqual(proizvod.kolicina, 0)
        self.assertFalse(proizvod.dostupan)
        self.assertEqual(Narudzba.objects.count(), 1)

    def test_kupovina_proizvoda_bez_zaliha(self):
        korisnik = User.objects.create_user(
            username="kupac_bez_zaliha",
            password="test12345"
        )

        self.client.force_login(korisnik)
        proizvod = Proizvod.objects.create(
            naziv="Mlijeko",
            kolicina=0,
            cijena=2.50,
            opis="Svježe mlijeko",
            slika="proizvodi/test_mlijeko.jpg",
            kategorija="Mliječni proizvodi",
            dostupan=False
        )

        session = self.client.session
        session["korpa"] = {str(proizvod.id): 1}
        session.save()

        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertContains(
            odgovor,
            "Nema dovoljno proizvoda na stanju."
        )

        self.assertEqual(Narudzba.objects.count(), 0)
        self.assertEqual(StavkaNarudzbe.objects.count(), 0)

        proizvod.refresh_from_db()
        self.assertEqual(proizvod.kolicina, 0)
        self.assertFalse(proizvod.dostupan)

    def test_narudzba_obrisanog_proizvoda(self):
        korisnik = User.objects.create_user(
            username="kupac_obrisan_proizvod",
            password="test12345"
        )

        self.client.force_login(korisnik)

        proizvod = Proizvod.objects.create(
            naziv="Sok",
            kolicina=5,
            cijena=3.00,
            opis="Voćni sok",
            slika="proizvodi/test_sok.jpg",
            kategorija="Pića",
            dostupan=True
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "1"
        })
        proizvod.delete()

        odgovor = self.client.post("/narudzba/", {
            "ime": "Marko",
            "prezime": "Markovic",
            "adresa": "Test adresa 1",
            "grad": "Banja Luka",
            "postanski_broj": "78000",
            "telefon": "060123456",
            "email": "marko@example.com"
        })

        self.assertContains(
            odgovor,
            "Proizvod iz korpe više nije dostupan."
        )

        self.assertEqual(Narudzba.objects.count(), 0)
        self.assertEqual(StavkaNarudzbe.objects.count(), 0)

    def test_korpa_sa_obrisanim_proizvodom(self):
        proizvod = Proizvod.objects.create(
            naziv="Sok od jabuke",
            kolicina=5,
            cijena=3.00,
            opis="Prirodni sok od jabuke",
            slika="proizvodi/test_sok.jpg",
            kategorija="Pića",
            dostupan=True
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "1"
        })

        proizvod.delete()
        odgovor = self.client.get("/korpa/")

        self.assertEqual(odgovor.status_code, 200)
        self.assertEqual(len(odgovor.context["stavke_korpe"]), 0)
        self.assertEqual(odgovor.context["ukupno_korpa"], 0)

    def test_uklanjanje_obrisanog_proizvoda_iz_sesije(self):
        proizvod = Proizvod.objects.create(
            naziv="Sok od narandže",
            kolicina=5,
            cijena=3.50,
            opis="Prirodni sok od narandže",
            slika="proizvodi/test_sok.jpg",
            kategorija="Pića",
            dostupan=True
        )

        self.client.post("/korpa/", {
            "proizvod_id": proizvod.id,
            "kolicina": "1"
        })

        proizvod.delete()

        self.client.get("/korpa/")
        self.assertEqual(self.client.session.get("korpa", {}), {})

    def test_pretraga_proizvoda(self):
        proizvod = Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje pretrage",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test miš",
            kolicina=3,
            cijena=25,
            opis="Miš za testiranje pretrage",
            slika="proizvodi/test_mis.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        odgovor = self.client.get("/", {"pretraga": "laptop"})

        self.assertContains(odgovor, "Test laptop")
        self.assertNotContains(odgovor, "Test miš")

    def test_filtriranje_po_kategoriji(self):
        Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje kategorije",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test miš",
            kolicina=3,
            cijena=25,
            opis="Miš za testiranje kategorije",
            slika="proizvodi/test_mis.jpg",
            kategorija="Računarska oprema",
            dostupan=True
        )

        odgovor = self.client.get(
            "/",
            {"kategorija": "Elektronika"}
        )
        self.assertContains(odgovor, "Test laptop")
        self.assertNotContains(odgovor, "Test miš")

    def test_sortiranje_po_cijeni(self):

        Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje sortiranja",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test miš",
            kolicina=3,
            cijena=25,
            opis="Miš za testiranje sortiranja",
            slika="proizvodi/test_mis.jpg",
            kategorija="Računarska oprema",
            dostupan=True
        )

        odgovor = self.client.get(
            "/",
            {"sortiranje": "cijena_rastuce"}
        )

        proizvodi = list(odgovor.context["proizvodi"])
        self.assertEqual(proizvodi[0].naziv, "Test miš")
        self.assertEqual(proizvodi[1].naziv, "Test laptop")
        odgovor = self.client.get(
            "/",
            {"sortiranje": "cijena_opadajuce"}
        )

        proizvodi = list(odgovor.context["proizvodi"])

        self.assertEqual(proizvodi[0].naziv, "Test laptop")
        self.assertEqual(proizvodi[1].naziv, "Test miš")

    def test_kombinacija_filtera(self):

        Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje filtera",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test miš",
            kolicina=3,
            cijena=25,
            opis="Miš za testiranje filtera",
            slika="proizvodi/test_mis.jpg",
            kategorija="Računarska oprema",
            dostupan=True
        )

        odgovor = self.client.get(
            "/",
            {"pretraga": "laptop", "kategorija": "Elektronika"}
        )

        proizvodi = list(odgovor.context["proizvodi"])

        self.assertEqual(len(proizvodi), 1)
        self.assertEqual(proizvodi[0].naziv, "Test laptop")

        odgovor = self.client.get(
            "/",
            {"pretraga": "laptop", "kategorija": "Računarska oprema"}
        )

        proizvodi = list(odgovor.context["proizvodi"])
        self.assertEqual(len(proizvodi), 0)

    def test_pretraga_i_sortiranje(self):
        Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test laptop mini",
            kolicina=3,
            cijena=600,
            opis="Manji laptop za testiranje",
            slika="proizvodi/test_laptop_mini.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test miš",
            kolicina=4,
            cijena=25,
            opis="Miš za testiranje pretrage",
            slika="proizvodi/test_mis.jpg",
            kategorija="Računarska oprema",
            dostupan=True
        )

        odgovor = self.client.get(
            "/",
            {"pretraga": "laptop", "sortiranje": "cijena_rastuce"}
        )

        proizvodi = list(odgovor.context["proizvodi"])

        self.assertEqual(len(proizvodi), 2)
        self.assertEqual(proizvodi[0].naziv, "Test laptop mini")
        self.assertEqual(proizvodi[1].naziv, "Test laptop")

    def test_sva_tri_filtera(self):
        Proizvod.objects.create(
            naziv="Test laptop",
            kolicina=5,
            cijena=1200,
            opis="Laptop za testiranje tri filtera",
            slika="proizvodi/test_laptop.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test laptop mini",
            kolicina=3,
            cijena=600,
            opis="Manji laptop za testiranje tri filtera",
            slika="proizvodi/test_laptop_mini.jpg",
            kategorija="Elektronika",
            dostupan=True
        )

        Proizvod.objects.create(
            naziv="Test laptop torba",
            kolicina=4,
            cijena=50,
            opis="Torba za laptop za testiranje tri filtera",
            slika="proizvodi/test_torba.jpg",
            kategorija="Računarska oprema",
            dostupan=True
        )

        odgovor = self.client.get(
            "/",
            {
                "pretraga": "laptop",
                "kategorija": "Elektronika",
                "sortiranje": "cijena_rastuce"
            }
        )

        proizvodi = list(odgovor.context["proizvodi"])

        self.assertEqual(len(proizvodi), 2)
        self.assertEqual(proizvodi[0].naziv, "Test laptop mini")
        self.assertEqual(proizvodi[1].naziv, "Test laptop")