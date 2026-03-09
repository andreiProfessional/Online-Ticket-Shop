from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.paginator import Paginator
from aplicatie_magazin_bilete.models import Accesare, Eveniment, CategorieEveniment, Utilizator
from aplicatie_magazin_bilete.middleware import MiddlewareLogAccesari
from datetime import timedelta, date
from .forms import FiltruProduseForm, ContactForm, InregistrareForm, LoginForm, SchimbareParolaForm
from dateutil.relativedelta import relativedelta
import re
import os
import json
import time


def home(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/home.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def info(request):
    def informatii_timp(parametru_timp):
        LUNI_AN = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]
        ZILE_SAPTAMANA = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
        TIMP_ACTUAL = timezone.localtime()
        rezultat = dict().fromkeys(["zi_saptamana", "zi_luna", "luna", "an", "ora"])
        if parametru_timp == "zi":
            rezultat["zi_saptamana"] = ZILE_SAPTAMANA[TIMP_ACTUAL.weekday()]
            rezultat["zi_luna"] = TIMP_ACTUAL.day
            rezultat["luna"] = LUNI_AN[TIMP_ACTUAL.month - 1]
            rezultat["an"] = TIMP_ACTUAL.year
        elif parametru_timp == "ora":
            rezultat["ora"] = TIMP_ACTUAL.strftime("%H:%M:%S")
        else:
            rezultat["zi_saptamana"] = ZILE_SAPTAMANA[TIMP_ACTUAL.weekday()]
            rezultat["zi_luna"] = TIMP_ACTUAL.day
            rezultat["luna"] = LUNI_AN[TIMP_ACTUAL.month - 1]
            rezultat["an"] = TIMP_ACTUAL.year
            rezultat["ora"] = TIMP_ACTUAL.strftime("%H:%M:%S")
        return rezultat

    timp = informatii_timp(request.GET.get("timp"))
    accesare = Accesare(request.META.get("REMOTE_ADDR"), request.get_full_path())
    parametri = list(request.GET.keys())
    numar_parametri = len(parametri)
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, "aplicatie_magazin_bilete/info.html", {
        "timp": timp,
        "accesare": accesare,
        "parametri": parametri,
        "numar_parametri": numar_parametri,
        "user_ip": user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def log(request):
    OPTIUNI_TABEL = ['id', 'ip', 'pagina', 'url', 'data']
    
    eroare = None
    numar_total_accesari = None
    detalii_accesari = None
    coloane_tabel = None
    
    parametru_accesari = request.GET.get("accesari")
    if parametru_accesari == "nr":
        numar_total_accesari = len(MiddlewareLogAccesari.accesari)
    if parametru_accesari == "detalii":
        detalii_accesari = MiddlewareLogAccesari.accesari
    
    parametru_tabel = request.GET.get("tabel")
    if parametru_tabel:
        if parametru_tabel == "tot":
            coloane_tabel = OPTIUNI_TABEL
        else:
            coloane_cerute = [col.strip() for col in parametru_tabel.split(",") if col.strip()]
            coloane_invalide = [col for col in coloane_cerute if col not in OPTIUNI_TABEL]
            if coloane_invalide:
                eroare = f"Coloane invalide: {', '.join(coloane_invalide)}. Coloane disponibile: {', '.join(OPTIUNI_TABEL)}"
            else:
                coloane_tabel = coloane_cerute
    
    lista_accesari = list(MiddlewareLogAccesari.accesari)
    
    parametru_iduri = request.GET.getlist("iduri")
    if parametru_iduri:
        lista_iduri = []
        for parametru in parametru_iduri:
            try:
                id_uri = [int(id_val.strip()) for id_val in parametru.split(",") if id_val.strip()]
                lista_iduri.extend(id_uri)
            except ValueError:
                eroare = "Parametrul \"iduri\" trebuie să conțină doar valori numerice întregi separate prin virgulă."
                lista_accesari = []
        
        if eroare is None:
            dubluri = request.GET.get("dubluri", "false")
            if dubluri.lower() != "true":
                multime_iduri = set()
                lista_iduri = [id_val for id_val in lista_iduri if not (id_val in multime_iduri or multime_iduri.add(id_val))]
            
            id_to_accesare = {accesare.id: accesare for accesare in MiddlewareLogAccesari.accesari}
            lista_accesari = [id_to_accesare[id_val] for id_val in lista_iduri if id_val in id_to_accesare]
    elif request.GET.get("ultimele") is not None:
        ultimele = request.GET.get("ultimele")
        try:
            ultimele = int(ultimele)
        except ValueError:
            eroare = "Parametrul \"ultimele\" trebuie să fie un o valoare numerică întregă."
            lista_accesari = []
        
        if eroare is None:
            numar_accesari = len(lista_accesari)
            if ultimele > numar_accesari:
                eroare = f"Au fost cerute {ultimele} accesări, dar există doar {numar_accesari}!"
            else:
                lista_accesari = lista_accesari[-ultimele:]
    
    if lista_accesari:
        lista_accesari = list(reversed(lista_accesari))
    
    pagina_mai_accesata = None
    pagina_mai_putin_accesata = None
    
    if MiddlewareLogAccesari.accesari:
        pagini_accesate = {}
        for accesare in MiddlewareLogAccesari.accesari:
            pagini_accesate[accesare.pagina] = pagini_accesate.get(accesare.pagina, 0) + 1
        if pagini_accesate:
            pagini_sortate = sorted(pagini_accesate.items(), key=lambda x: x[1], reverse=True)
            pagina_mai_accesata = pagini_sortate[0][0]
            if len(pagini_sortate) > 1 and pagini_sortate[0][1] != pagini_sortate[-1][1]:
                pagina_mai_putin_accesata = pagini_sortate[-1][0]
    
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, "aplicatie_magazin_bilete/log.html", {
        "accesari": lista_accesari,
        "eroare": eroare,
        "numar_total_accesari": numar_total_accesari,
        "detalii_accesari": detalii_accesari,
        "coloane_tabel": coloane_tabel,
        "pagina_mai_accesata": pagina_mai_accesata,
        "pagina_mai_putin_accesata": pagina_mai_putin_accesata,
        "user_ip": user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def despre(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/despre.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def produse(request):
    ordine_sortare = request.GET.get('sort', 'a')
    if ordine_sortare == 'd':
        ordine = ['-nume']
    else:
        ordine = ['nume']
    
    form_filtru = FiltruProduseForm(request.GET or None)
    
    lista_evenimente = Eveniment.objects.select_related('locatie', 'organizator', 'categorie')
    
    if form_filtru.is_valid():
        nume = form_filtru.cleaned_data.get('nume')
        if nume:
            lista_evenimente = lista_evenimente.filter(nume__icontains=nume)
        
        data_min = form_filtru.cleaned_data.get('data_min')
        if data_min:
            lista_evenimente = lista_evenimente.filter(data__gte=data_min)
        
        data_max = form_filtru.cleaned_data.get('data_max')
        if data_max:
            lista_evenimente = lista_evenimente.filter(data__lte=data_max)
        
        ora_min = form_filtru.cleaned_data.get('ora_min')
        if ora_min:
            lista_evenimente = lista_evenimente.filter(ora__gte=ora_min)
        
        ora_max = form_filtru.cleaned_data.get('ora_max')
        if ora_max:
            lista_evenimente = lista_evenimente.filter(ora__lte=ora_max)
        
        durata_min_h = form_filtru.cleaned_data.get('durata_min_h')
        if durata_min_h is not None:
            lista_evenimente = lista_evenimente.filter(durata__gte=timedelta(hours=durata_min_h))
        
        durata_max_h = form_filtru.cleaned_data.get('durata_max_h')
        if durata_max_h is not None:
            lista_evenimente = lista_evenimente.filter(durata__lte=timedelta(hours=durata_max_h))
        
        categorie = form_filtru.cleaned_data.get('categorie')
        if categorie:
            lista_evenimente = lista_evenimente.filter(categorie=categorie)
        
        organizator = form_filtru.cleaned_data.get('organizator')
        if organizator:
            lista_evenimente = lista_evenimente.filter(organizator=organizator)
        
        locatie = form_filtru.cleaned_data.get('locatie')
        if locatie:
            lista_evenimente = lista_evenimente.filter(locatie=locatie)
        
        capacitate_min = form_filtru.cleaned_data.get('capacitate_min')
        if capacitate_min is not None:
            lista_evenimente = lista_evenimente.filter(locatie__capacitate__gte=capacitate_min)
        
        capacitate_max = form_filtru.cleaned_data.get('capacitate_max')
        if capacitate_max is not None:
            lista_evenimente = lista_evenimente.filter(locatie__capacitate__lte=capacitate_max)
    
    lista_evenimente = lista_evenimente.order_by(*ordine)
    
    elemente_per_pagina = int(request.GET.get('elemente_per_pagina', '9'))
    
    paginare_schimbata = False
    paginare_anterioara = request.session.get('elemente_per_pagina')
    if paginare_anterioara and paginare_anterioara != str(elemente_per_pagina):
        paginare_schimbata = True
    request.session['elemente_per_pagina'] = str(elemente_per_pagina)
    
    paginator = Paginator(lista_evenimente, elemente_per_pagina)
    numar_pagina = request.GET.get('page', 1)
    pagina_evenimente = paginator.get_page(numar_pagina)
    
    ip_utilizator = request.META.get('REMOTE_ADDR')
    
    return render(request, 'aplicatie_magazin_bilete/produse.html', {
        'pagina_evenimente': pagina_evenimente,
        'ip_utilizator': ip_utilizator,
        'ordine_sortare': ordine_sortare,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form_filtru': form_filtru,
        'paginare_schimbata': paginare_schimbata,
    })

def eveniment_detalii(request, id_eveniment):
    eveniment = get_object_or_404(
        Eveniment.objects.select_related('organizator', 'locatie', 'categorie')
                         .prefetch_related('bilete__categorii'),
        id_eveniment=id_eveniment
    )
    ip_utilizator = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/eveniment_detalii.html', {
        'eveniment': eveniment,
        'ip_utilizator': ip_utilizator,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def contact(request):
    def calculate_age_string(data_nasterii):
        if not data_nasterii:
            return "N/A"
        today = date.today()
        age_delta = relativedelta(today, data_nasterii)
        return f"{age_delta.years} ani și {age_delta.months} luni"
    
    def normalize_message(mesaj):
        if not mesaj:
            return mesaj
        mesaj = mesaj.replace('\n', ' ').replace('\r', ' ')
        mesaj = re.sub(r'\s+', ' ', mesaj).strip()
        return mesaj
    
    def capitalize_after_punctuation(mesaj):
        if not mesaj:
            return mesaj
        def replacement_func(match):
            return match.group(1) + match.group(2) + match.group(3).upper()
        mesaj = re.sub(r'(\.\.\.|\.|[\?!])(\s+)([a-z])', replacement_func, mesaj)
        return mesaj
    
    def is_urgent(tip_mesaj, minim_zile_asteptare):
        if not tip_mesaj or minim_zile_asteptare is None:
            return False
        minimuri = {
            'review': 4,
            'cerere': 4,
            'intrebare': 2,
            'reclamatie': 1,
            'programare': 1,
        }
        minim_necesar = minimuri.get(tip_mesaj)
        if minim_necesar is None:
            return False
        return minim_zile_asteptare == minim_necesar
    
    def preprocess_contact_data(cleaned_data):
        data = cleaned_data.copy()
        data['varsta'] = calculate_age_string(cleaned_data.get('data_nasterii'))
        mesaj = cleaned_data.get('mesaj', '')
        mesaj = normalize_message(mesaj)
        mesaj = capitalize_after_punctuation(mesaj)
        data['mesaj'] = mesaj
        data['urgent'] = is_urgent(
            cleaned_data.get('tip_mesaj'),
            cleaned_data.get('minim_zile_asteptare')
        )
        return data
    
    def save_contact_to_file(data, request):
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dir_path = os.path.join(app_dir, 'Mesaje')
        os.makedirs(dir_path, exist_ok=True)
        timestamp_unix = int(time.time())
        urgent_suffix = '_urgent' if data.get('urgent') else ''
        filename = f'mesaj_{timestamp_unix}{urgent_suffix}.json'
        filepath = os.path.join(dir_path, filename)
        json_data = {
            'nume': data.get('nume'),
            'prenume': data.get('prenume'),
            'cnp': data.get('cnp'),
            'varsta': data.get('varsta'),
            'data_nasterii': str(data.get('data_nasterii')) if data.get('data_nasterii') else None,
            'email': data.get('email'),
            'tip_mesaj': data.get('tip_mesaj'),
            'subiect': data.get('subiect'),
            'minim_zile_asteptare': data.get('minim_zile_asteptare'),
            'mesaj': data.get('mesaj'),
            'urgent': data.get('urgent'),
            'ip_utilizator': request.META.get('REMOTE_ADDR'),
            'data_sosire': timezone.now().strftime('%Y-%m-%d'),
            'ora_sosire': timezone.now().strftime('%H:%M:%S'),
            'timestamp_sosire': timestamp_unix,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        return filepath
    
    succes = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = preprocess_contact_data(form.cleaned_data)
            save_contact_to_file(data, request)
            succes = True
            form = ContactForm()
    else:
        form = ContactForm()
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/contact.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form': form,
        'succes': succes,
    })

def cos_virtual(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/cos_virtual.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def sponsori(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/sponsori.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def intrebari_frecvente(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/intrebari_frecvente.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire')
    })

def categorie(request, nume_categorie):
    categorie_obj = get_object_or_404(CategorieEveniment, denumire=nume_categorie)
    
    ordine_sortare = request.GET.get('sort', 'a')
    if ordine_sortare == 'd':
        ordine = ['-nume']
    else:
        ordine = ['nume']
    
    data_formular = request.GET.copy()
    data_formular['categorie'] = categorie_obj.id
    form_filtru = FiltruProduseForm(data_formular)
    
    lista_evenimente = Eveniment.objects.filter(
        categorie=categorie_obj
    ).select_related('locatie', 'organizator', 'categorie')
    
    eroare_categorie = None
    
    if form_filtru.is_valid():
        categorie_formular = form_filtru.cleaned_data.get('categorie')
        if categorie_formular and categorie_formular.id != categorie_obj.id:
            eroare_categorie = (
                f"⚠️ Atenție! Categoria selectată ({categorie_formular.denumire}) "
                f"nu corespunde cu categoria paginii ({categorie_obj.denumire}). "
                f"Filtrarea se va face pentru categoria corectă: {categorie_obj.denumire}."
            )
        
        nume = form_filtru.cleaned_data.get('nume')
        if nume:
            lista_evenimente = lista_evenimente.filter(nume__icontains=nume)
        
        data_min = form_filtru.cleaned_data.get('data_min')
        if data_min:
            lista_evenimente = lista_evenimente.filter(data__gte=data_min)
        
        data_max = form_filtru.cleaned_data.get('data_max')
        if data_max:
            lista_evenimente = lista_evenimente.filter(data__lte=data_max)
        
        ora_min = form_filtru.cleaned_data.get('ora_min')
        if ora_min:
            lista_evenimente = lista_evenimente.filter(ora__gte=ora_min)
        
        ora_max = form_filtru.cleaned_data.get('ora_max')
        if ora_max:
            lista_evenimente = lista_evenimente.filter(ora__lte=ora_max)
        
        durata_min_h = form_filtru.cleaned_data.get('durata_min_h')
        if durata_min_h is not None:
            lista_evenimente = lista_evenimente.filter(durata__gte=timedelta(hours=durata_min_h))
        
        durata_max_h = form_filtru.cleaned_data.get('durata_max_h')
        if durata_max_h is not None:
            lista_evenimente = lista_evenimente.filter(durata__lte=timedelta(hours=durata_max_h))
        
        organizator = form_filtru.cleaned_data.get('organizator')
        if organizator:
            lista_evenimente = lista_evenimente.filter(organizator=organizator)
        
        locatie = form_filtru.cleaned_data.get('locatie')
        if locatie:
            lista_evenimente = lista_evenimente.filter(locatie=locatie)
        
        capacitate_min = form_filtru.cleaned_data.get('capacitate_min')
        if capacitate_min is not None:
            lista_evenimente = lista_evenimente.filter(locatie__capacitate__gte=capacitate_min)
        
        capacitate_max = form_filtru.cleaned_data.get('capacitate_max')
        if capacitate_max is not None:
            lista_evenimente = lista_evenimente.filter(locatie__capacitate__lte=capacitate_max)
    
    lista_evenimente = lista_evenimente.order_by(*ordine)
    
    elemente_per_pagina = int(request.GET.get('elemente_per_pagina', '9'))
    
    paginare_schimbata = False
    paginare_anterioara = request.session.get('elemente_per_pagina')
    if paginare_anterioara and paginare_anterioara != str(elemente_per_pagina):
        paginare_schimbata = True
    request.session['elemente_per_pagina'] = str(elemente_per_pagina)
    
    paginator = Paginator(lista_evenimente, elemente_per_pagina)
    numar_pagina = request.GET.get('page', 1)
    pagina_evenimente = paginator.get_page(numar_pagina)
    
    ip_utilizator = request.META.get('REMOTE_ADDR')
    
    return render(request, 'aplicatie_magazin_bilete/produse.html', {
        'pagina_evenimente': pagina_evenimente,
        'ip_utilizator': ip_utilizator,
        'ordine_sortare': ordine_sortare,
        'categorie_curenta': categorie_obj,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form_filtru': form_filtru,
        'paginare_schimbata': paginare_schimbata,
        'eroare_categorie': eroare_categorie,
    })

def inregistrare(request):
    """View pentru formularul de înregistrare utilizator"""
    succes = False
    mesaj_succes = ""
    
    if request.method == 'POST':
        form = InregistrareForm(request.POST)
        if form.is_valid():
            # Creează utilizatorul
            utilizator = Utilizator(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                parola=make_password(form.cleaned_data['parola']),  # Hash parola
                nume=form.cleaned_data['nume'],
                tip_cont=form.cleaned_data['tip_cont'],
                tara=form.cleaned_data.get('tara') or None,
                cnp=form.cleaned_data.get('cnp') or None,
                telefon=form.cleaned_data.get('telefon') or None,
                poza=form.cleaned_data.get('poza') or None,
            )
            utilizator.save()
            
            succes = True
            mesaj_succes = f"Contul pentru {utilizator.username} a fost creat cu succes!"
            form = InregistrareForm()  # Reset formular după succes
    else:
        form = InregistrareForm()
    
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/inregistrare.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form': form,
        'succes': succes,
        'mesaj_succes': mesaj_succes,
    })

def login(request):
    eroare = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            parola = form.cleaned_data['parola']
            remember_me = form.cleaned_data['remember_me']
            
            utilizator = None
            try:
                utilizator = Utilizator.objects.get(username=username_or_email)
            except Utilizator.DoesNotExist:
                try:
                    utilizator = Utilizator.objects.get(email=username_or_email)
                except Utilizator.DoesNotExist:
                    pass
            
            if utilizator and check_password(parola, utilizator.parola):
                request.session['user_id'] = str(utilizator.id_utilizator)
                request.session['username'] = utilizator.username
                request.session['nume'] = utilizator.nume
                request.session['email'] = utilizator.email
                request.session['tip_cont'] = utilizator.tip_cont
                request.session['tara'] = utilizator.tara if utilizator.tara else None
                request.session['cnp'] = utilizator.cnp if utilizator.cnp else None
                request.session['telefon'] = utilizator.telefon if utilizator.telefon else None
                request.session['poza'] = utilizator.poza if utilizator.poza else None
                
                if remember_me:
                    # Ține minte utilizatorul timp de o zi (86400 secunde)
                    request.session.set_expiry(86400)
                else:
                    # Sesiunea expiră la închiderea browserului
                    request.session.set_expiry(0)
                
                return redirect('profil')
            else:
                eroare = "Nume utilizator/email sau parolă incorectă!"
    else:
        form = LoginForm()
    
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/login.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form': form,
        'eroare': eroare,
    })

def logout(request):
    request.session.flush()
    return redirect('home')

def profil(request):
    """View pentru pagina de profil - afișează datele utilizatorului din sesiune"""
    # Verifică dacă utilizatorul este autentificat
    if not request.session.get('user_id'):
        return redirect('login')
    
    # Preia datele din sesiune
    user_data = {
        'user_id': request.session.get('user_id'),
        'username': request.session.get('username'),
        'nume': request.session.get('nume'),
        'email': request.session.get('email'),
        'tip_cont': request.session.get('tip_cont'),
        'tara': request.session.get('tara'),
        'cnp': request.session.get('cnp'),
        'telefon': request.session.get('telefon'),
        'poza': request.session.get('poza'),
    }
    
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/profil.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'user_data': user_data,
    })

def schimbare_parola(request):
    """View pentru schimbarea parolei utilizatorului"""
    # Verifică dacă utilizatorul este autentificat
    if not request.session.get('user_id'):
        return redirect('login')
    
    succes = False
    eroare = None
    
    if request.method == 'POST':
        form = SchimbareParolaForm(request.POST)
        if form.is_valid():
            parola_veche = form.cleaned_data['parola_veche']
            parola_noua = form.cleaned_data['parola_noua']
            
            # Găsește utilizatorul în baza de date
            try:
                utilizator = Utilizator.objects.get(id_utilizator=request.session.get('user_id'))
                
                # Verifică parola veche
                if check_password(parola_veche, utilizator.parola):
                    # Actualizează parola
                    utilizator.parola = make_password(parola_noua)
                    utilizator.save()
                    
                    succes = True
                    form = SchimbareParolaForm()  # Reset formular
                else:
                    eroare = "Parola actuală este incorectă!"
            except Utilizator.DoesNotExist:
                eroare = "Utilizatorul nu a fost găsit!"
    else:
        form = SchimbareParolaForm()
    
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'aplicatie_magazin_bilete/schimbare_parola.html', {
        'user_ip': user_ip,
        'categorii_evenimente': CategorieEveniment.objects.all().order_by('denumire'),
        'form': form,
        'succes': succes,
        'eroare': eroare,
    })
