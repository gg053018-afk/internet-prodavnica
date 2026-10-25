from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings

class RegistracijaTest(TestCase):

    def test_stranica_registracije(self):
        odgovor = self.client.get("/registracija/")
        self.assertEqual(odgovor.status_code, 200)

    def test_registracija_korisnika(self):
        odgovor = self.client.post("/registracija/", {
            "korisnicko_ime": "testkorisnik",
            "e_mail": "test@example.com",
            "lozinka": "Test12345!",
            "potvrda_lozinke": "Test12345!"
        })
        self.assertEqual(odgovor.status_code, 302)

        korisnik = User.objects.get(username="testkorisnik")

        self.assertEqual(korisnik.email, "test@example.com")
        self.assertFalse(korisnik.is_active)

    def test_slanje_aktivacionog_emaila(self):
        self.client.post("/registracija/", {
            "korisnicko_ime": "testemail",
            "e_mail": "testemail@example.com",
            "lozinka": "Test12345!",
            "potvrda_lozinke": "Test12345!"
        })
        self.assertEqual(len(mail.outbox), 1)

    def test_aktivacija_korisnika(self):
        korisnik = User.objects.create_user(
            username="testaktivacija",
            email="aktivacija@example.com",
            password="Test12345!",
            is_active=False
        )

        uid = urlsafe_base64_encode(force_bytes(korisnik.pk))
        token = default_token_generator.make_token(korisnik)
        link = reverse("aktivacija", kwargs={"uidb64": uid, "token": token})
        odgovor = self.client.get(link)
        korisnik.refresh_from_db()

        self.assertTrue(korisnik.is_active)

    def test_prijava_aktivnog_korisnika(self):
        korisnik = User.objects.create_user(
            username="testprijava",
            email="prijava@example.com",
            password="Test12345!",
            is_active=True
        )

        odgovor = self.client.post("/prijava/", {
            "korisnicko_ime": "testprijava",
            "lozinka": "Test12345!"
        })

        self.assertEqual(odgovor.status_code, 302)

        self.assertTrue(
            odgovor.wsgi_request.user.is_authenticated
        )

        self.assertEqual(
            odgovor.wsgi_request.user.username,
            "testprijava"
        )

    def test_prijava_neaktivnog_korisnika(self):
        korisnik = User.objects.create_user(
            username="testneaktivan",
            email="neaktivan@example.com",
            password="Test12345!",
            is_active=False
        )

        odgovor = self.client.post("/prijava/", {
            "korisnicko_ime": "testneaktivan",
            "lozinka": "Test12345!"
        })

        self.assertEqual(odgovor.status_code, 200)

        self.assertFalse(
            odgovor.wsgi_request.user.is_authenticated
        )
        self.assertFalse(korisnik.is_active)

    def test_odjava_korisnika(self):
        korisnik = User.objects.create_user(
            username="testodjava",
            email="odjava@example.com",
            password="Test12345!",
            is_active=True
        )

        self.client.login(
            username="testodjava",
            password="Test12345!"
        )

        odgovor = self.client.get("/odjava/")

        self.assertEqual(odgovor.status_code, 302)

        self.assertFalse(
            odgovor.wsgi_request.user.is_authenticated
        )

    @override_settings(DEMO_MODE=True)
    def test_demo_registracija(self):
        odgovor = self.client.post("/registracija/", {
            "korisnicko_ime": "demo_test",
            "e_mail": "demo_test@example.com",
            "lozinka": "Test12345!",
            "potvrda_lozinke": "Test12345!"
        })

        self.assertRedirects(odgovor, reverse("demo_aktivacija"))
        korisnik = User.objects.get(username="demo_test")

        self.assertFalse(korisnik.is_active)
        self.assertIn("demo_aktivacioni_link", self.client.session)

        odgovor = self.client.get(reverse("demo_aktivacija"))
        self.assertEqual(odgovor.status_code, 200)

        aktivacioni_link = self.client.session["demo_aktivacioni_link"]
        odgovor = self.client.get(aktivacioni_link)

        korisnik.refresh_from_db()
        self.assertTrue(korisnik.is_active)
        self.assertNotIn("demo_aktivacioni_link", self.client.session)
        self.assertNotIn("demo_korisnik_id", self.client.session)
        self.assertNotIn("demo_token", self.client.session)

    @override_settings(DEMO_MODE=True)
    def test_demo_aktivacija_tudjeg_naloga(self):
        drugi_korisnik = User.objects.create_user(
            username="drugi_demo",
            email="drugi_demo@example.com",
            password="Test12345!"
        )
        drugi_korisnik.is_active = False
        drugi_korisnik.save()

        token = default_token_generator.make_token(drugi_korisnik)
        uid = urlsafe_base64_encode(force_bytes(drugi_korisnik.pk))

        aktivacioni_link = reverse(
            "aktivacija",
            kwargs={"uidb64": uid, "token": token}
        )
        odgovor = self.client.get(aktivacioni_link)
        self.assertContains(odgovor, "Demo aktivacija nije dozvoljena.")

        drugi_korisnik.refresh_from_db()
        self.assertFalse(drugi_korisnik.is_active)

    @override_settings(DEMO_MODE=False)
    def test_demo_stranica_iskljucena(self):
        odgovor = self.client.get(reverse("demo_aktivacija"))
        
        self.assertContains(odgovor, "Demo aktivacija nije dostupna.")

    @override_settings(DEMO_MODE=True)
    def test_demo_aktivacija_pogresnog_korisnika(self):
        
        prvi_korisnik = User.objects.create_user(
            username="prvi_demo",
            email="prvi_demo@example.com",
            password="Test12345!"
        )
        
        drugi_korisnik = User.objects.create_user(
            username="drugi_demo",
            email="drugi_demo@example.com",
            password="Test12345!"
        )

        drugi_korisnik.is_active = False
        drugi_korisnik.save()

        self.client.force_login(prvi_korisnik)

        response = self.client.get(
            "/demo-aktivacija/",
            {"user_id": drugi_korisnik.id}
        )

        self.assertContains(
            response,
            "Demo aktivacioni link nije pronađen."
        )

        drugi_korisnik.refresh_from_db()

        self.assertFalse(drugi_korisnik.is_active) 