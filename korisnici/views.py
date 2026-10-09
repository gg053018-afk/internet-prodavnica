from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

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
            poruka = "Pogrešno korisničko ime ili lozinka"

    return render(
        request,
        "korisnici/prijava.html",
        {"poruka": poruka}
    )

def odjava(request):
    logout(request)
    return redirect("/")