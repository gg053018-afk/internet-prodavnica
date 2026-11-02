# Internet prodavnica

## Opis projekta

Internet prodavnica je web aplikacija izrađena pomoću Pythona i Django frameworka.

Aplikacija omogućava pregled i pretragu proizvoda, registraciju korisnika, dodavanje proizvoda u korpu i kreiranje narudžbi.

Projekat je namijenjen demonstraciji programerskih vještina i ne predstavlja stvarnu prodavnicu.

## Korištene tehnologije

- Python
- Django 6.1.2
- HTML5
- CSS3
- SQLite
- Git i GitHub
- PythonAnywhere (hosting)

## Funkcionalnosti

- Registracija i prijava korisnika
- DEMO aktivacija korisničkog naloga
- Pregled proizvoda i njihovih detalja
- Pretraga proizvoda po nazivu
- Filtriranje proizvoda po kategoriji
- Sortiranje proizvoda po cijeni
- Paginacija proizvoda
- Dodavanje i uklanjanje proizvoda iz korpe
- Promjena količine proizvoda u korpi
- Provjera dostupnih zaliha
- Kreiranje narudžbi
- Pregled vlastitih narudžbi i njihovih statusa
- Administracija proizvoda i narudžbi
- Prilagođen prikaz za mobilne uređaje
- Automatski Django testovi

## DEMO verzija

Javna verzija projekta dostupna je na adresi:

https://usergoran.pythonanywhere.com/

Ovo je demonstracijska Internet prodavnica. Proizvodi i narudžbe služe isključivo za testiranje.

Korisnici mogu napraviti testni nalog i aktivirati ga putem DEMO aktivacionog linka, bez slanja stvarnog e-maila.

## Pokretanje projekta lokalno

Za pokretanje projekta potrebno je instalirati Python i Git.

Preuzimanje projekta:

```bash
git clone https://github.com/gg053018-afk/internet-prodavnica.git
```

Ulazak u direktorij projekta:

```bash
cd internet-prodavnica
```

Kreiranje virtualnog okruženja na Windowsu:

```powershell
python -m venv venv
```

Aktiviranje virtualnog okruženja:

```powershell
.\venv\Scripts\Activate.ps1
```

Instaliranje potrebnih biblioteka:

```bash
pip install -r requirements.txt
```
### Podešavanje okruženja

U glavnom direktoriju projekta napraviti datoteku `.env`.

U nju dodati sljedeća podešavanja:

```env
SECRET_KEY=ovdje_unijeti_vlastiti_tajni_kljuc
DJANGO_DEBUG=True
DJANGO_DEMO_MODE=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Za `SECRET_KEY` potrebno je generisati vlastiti sigurni ključ.

Datoteka `.env` ne smije se objavljivati na GitHubu jer sadrži osjetljive podatke.

### Priprema baze podataka

Nakon podešavanja `.env` datoteke, izvršiti migracije:

```bash
python manage.py migrate
```

### Pokretanje aplikacije

Pokrenuti Django razvojni server:

```bash
python manage.py runserver
```

Nakon pokretanja otvoriti adresu:

http://127.0.0.1:8000/

### Pokretanje automatskih testova

Za provjeru funkcionalnosti projekta pokrenuti:

```bash
python manage.py test
```

Projekat trenutno sadrži 40 automatskih testova.