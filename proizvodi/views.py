from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Proizvod, Narudzba, StavkaNarudzbe

def pocetna(request):
    proizvodi = Proizvod.objects.all()
    return render(request, "proizvodi/pocetna.html", {"proizvodi": proizvodi})

def detalji_proizvoda(request, proizvod_id):
    poruka = ""
    proizvod = Proizvod.objects.get(id=proizvod_id)

    if request.method == "POST":
        kolicina = request.POST.get("kolicina")

        try:
            kolicina = int(kolicina)
        except (TypeError, ValueError):
            poruka = "Unesite ispravnu količinu."
        else:
            if not proizvod.dostupan or proizvod.kolicina == 0:
                poruka = "Proizvod nije dostupan."

            elif kolicina < 1 or kolicina > proizvod.kolicina:
                poruka = "Neispravna količina ili nema dovoljno proizvoda na stanju."

            else:
                korpa = request.session.get("korpa", {})
                proizvod_id_str = str(proizvod_id)

                if proizvod_id_str in korpa:
                    nova_kolicina = korpa[proizvod_id_str] + kolicina

                    if nova_kolicina > proizvod.kolicina:
                        poruka = "Nema dovoljno proizvoda na stanju."
                    else:
                        korpa[proizvod_id_str] = nova_kolicina
                        poruka = "Proizvod je dodat u korpu."
                else:
                    korpa[proizvod_id_str] = kolicina
                    poruka = "Proizvod je dodat u korpu."

                request.session["korpa"] = korpa

    return render(
        request,
        "proizvodi/detalji_proizvoda.html",
        {"proizvod": proizvod, "poruka": poruka}
    )
def korpa(request):
    korpa_session = request.session.get("korpa", {})

    if request.method == "POST":
        akcija = request.POST.get("akcija")
        proizvod_id = request.POST.get("proizvod_id")

        if akcija == "ukloni":
            if str(proizvod_id) in korpa_session:
                del korpa_session[str(proizvod_id)]
                request.session["korpa"] = korpa_session
                messages.success(request, "Proizvod je uspješno uklonjen iz korpe.")

        else:
            kolicina = request.POST.get("kolicina")
            kolicina = int(kolicina)
            proizvod = Proizvod.objects.get(id=proizvod_id)

            if kolicina >= 1 and kolicina <= proizvod.kolicina:
                korpa_session[str(proizvod_id)] = kolicina

                request.session["korpa"] = korpa_session

    stavke_korpe = []
    ukupno_korpa = 0

    for proizvod_id, kolicina in korpa_session.items():
        proizvod = Proizvod.objects.get(id=proizvod_id)
        ukupno = proizvod.cijena * kolicina
        ukupno_korpa += ukupno
        stavke_korpe.append({
            "proizvod": proizvod,
            "kolicina": kolicina,
            "ukupno": ukupno,
        })

    return render(request, "proizvodi/korpa.html",
    {
        "stavke_korpe": stavke_korpe,
        "ukupno_korpa": ukupno_korpa
    })

@login_required(login_url="prijava")
def narudzba(request):
    poruka = ""

    if request.method == "POST":
        ime = request.POST.get("ime")
        prezime = request.POST.get("prezime")
        adresa = request.POST.get("adresa")
        grad = request.POST.get("grad")
        postanski_broj = request.POST.get("postanski_broj")
        telefon = request.POST.get("telefon")
        email = request.POST.get("email")

        if not all([ime, prezime, adresa, grad, postanski_broj, telefon, email]):
            poruka = "Morate popuniti sva obavezna polja."

            return render(
                request,
                "proizvodi/narudzba.html",
                {"poruka": poruka}
            )

        korpa_session = request.session.get("korpa", {})

        if not korpa_session:
            poruka = "Korpa je prazna."
            return render(
                request,
                "proizvodi/narudzba.html",
                {"poruka": poruka}
            )

        for proizvod_id, kolicina in korpa_session.items():
            proizvod = Proizvod.objects.get(id=proizvod_id)

            if kolicina < 1 or kolicina > proizvod.kolicina:
                poruka = "Nema dovoljno proizvoda na stanju."

                return render(
                    request,
                    "proizvodi/narudzba.html",
                    {"poruka": poruka}
                )

        narudzba = Narudzba.objects.create(
            korisnik=request.user,
            ime=ime,
            prezime=prezime,
            adresa=adresa,
            grad=grad,
            postanski_broj=postanski_broj,
            telefon=telefon,
            email=email
        )

        ukupno_narudzbe = 0

        for proizvod_id, kolicina in korpa_session.items():
            proizvod = Proizvod.objects.get(id=proizvod_id)

            ukupno_narudzbe += proizvod.cijena * kolicina

            StavkaNarudzbe.objects.create(
                narudzba=narudzba,
                proizvod=proizvod,
                kolicina=kolicina,
                cijena=proizvod.cijena
            )

            proizvod.kolicina -= kolicina

            if proizvod.kolicina == 0:
                proizvod.dostupan = False

            proizvod.save()

        narudzba.ukupno = ukupno_narudzbe
        narudzba.save()

        request.session["korpa"] = {}

        messages.success(request, "Narudžba je uspješno poslata!")

        return redirect("pocetna")

    return render(
        request,
        "proizvodi/narudzba.html",
        {"poruka": poruka}
    )


@login_required(login_url="prijava")
def moje_narudzbe(request):

    narudzbe = Narudzba.objects.filter(korisnik=request.user).order_by("-id")
    
    return render(
        request,
        "proizvodi/moje_narudzbe.html",
        {"narudzbe": narudzbe}
    )