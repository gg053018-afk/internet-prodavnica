from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponse

# Create your views here.

def registracija(request):
    poruka = ""
    if request.method == "POST":
        korisnicko_ime = request.POST.get("korisnicko_ime")
        e_mail = request.POST.get("e_mail")
        lozinka = request.POST.get("lozinka")
        potvrda_lozinke = request.POST.get("potvrda_lozinke")

        if lozinka == potvrda_lozinke:
            if User.objects.filter(username=korisnicko_ime).exists():
                poruka = "Korisničko ime već postoji"
            else:
                korisnik = User.objects.create_user(
                    username=korisnicko_ime,
                    email=e_mail,
                    password=lozinka
                )

                korisnik.is_active = False
                korisnik.save()
                token = default_token_generator.make_token(korisnik)
                uid = urlsafe_base64_encode(force_bytes(korisnik.pk))
                aktivacioni_url = reverse("aktivacija", kwargs={"uidb64": uid, "token": token})
                aktivacioni_link = request.build_absolute_uri(aktivacioni_url)
                send_mail(
                    "Aktivacija naloga",
                    f"Kliknite na link za aktivaciju naloga: {aktivacioni_link}",
                    "noreply@internetprodavnica.com",
                    [e_mail],
                )
                
                return redirect("/prijava/")
        else:
            poruka = "Lozinke nisu iste"

    return render(request, "korisnici/registracija.html",
    {"poruka": poruka})

def prijava(request):
    poruka = ""

    if request.method == "POST":
        korisnicko_ime = request.POST.get("korisnicko_ime")
        lozinka = request.POST.get("lozinka")

        korisnik = authenticate(
            request,
            username=korisnicko_ime,
            password=lozinka
        )

        if korisnik is not None:
            login(request, korisnik)
            sljedeca_stranica = request.POST.get("next") or request.GET.get("next", "/")

            if not url_has_allowed_host_and_scheme(
                url=sljedeca_stranica,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):

                sljedeca_stranica = "/"

            return redirect(sljedeca_stranica)
        else:
            neaktivni_korisnik = User.objects.filter(username=korisnicko_ime, is_active=False).first()
        
        if neaktivni_korisnik is not None and neaktivni_korisnik.check_password(lozinka):
            poruka = "Vaš nalog nije aktiviran. Provjerite e-mail i kliknite na aktivacioni link."

        else:
            poruka = "Pogrešno korisničko ime ili lozinka"

    return render(
        request,
        "korisnici/prijava.html",
        {"poruka": poruka}
    )

def odjava(request):
    sacuvana_korpa = request.session.get("korpa", {}).copy()

    logout(request)

    request.session["korpa"] = sacuvana_korpa

    return redirect("/")

def aktivacija(request, uidb64, token):
    try:
        korisnik_id = force_str(urlsafe_base64_decode(uidb64))
        korisnik = User.objects.filter(pk=korisnik_id).first()
    
    except (ValueError, TypeError, OverflowError, UnicodeDecodeError):
        korisnik = None
    
    if korisnik is not None and default_token_generator.check_token(korisnik, token):
        korisnik.is_active = True
        korisnik.save()
        
        return redirect("/prijava/")
    return HttpResponse("Aktivacioni link nije ispravan ili je istekao.")