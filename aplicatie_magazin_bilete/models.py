from django.db import models
from datetime import datetime
from urllib.parse import urlparse
import uuid



class CategorieBilet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    denumire = models.CharField(max_length=100)
    simbol = models.CharField(max_length=1, unique=True, choices=[(chr(c), chr(c)) for c in range(ord('A'), ord('Z') + 1)])
    
    def __str__(self):
        return f"{self.denumire} ({self.simbol})"


class CategorieEveniment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    denumire = models.CharField(max_length=100, unique=True)
    descriere = models.TextField()
    culoare = models.CharField(max_length=7, default='#667eea')
    
    def __str__(self):
        return self.denumire.upper()
    
    def get_url_name(self):
        return self.denumire


class Organizator(models.Model):
    id_organizator = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nume = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nume


class Locatie(models.Model):
    id_locatie = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nume = models.CharField(max_length=200)
    descriere = models.TextField(null=True, blank=True)
    capacitate = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nume}"


class Eveniment(models.Model):
    id_eveniment = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nume = models.CharField(max_length=200)
    descriere = models.TextField(null=True, blank=True)
    data = models.DateField()
    ora = models.TimeField()
    durata = models.DurationField()
    data_adaugare = models.DateTimeField(auto_now_add=True)
    url_imagine = models.URLField(max_length=500, blank=True, null=True, help_text="URL către imaginea evenimentului")
    
    organizator = models.ForeignKey(
        Organizator,
        on_delete=models.PROTECT,
        related_name='evenimente'
    )
    locatie = models.ForeignKey(
        Locatie,
        on_delete=models.PROTECT,
        related_name='evenimente'
    )
    categorie = models.ForeignKey(
        CategorieEveniment,
        on_delete=models.PROTECT,
        related_name='evenimente'
    )

    def __str__(self):
        return f"{self.nume} - {self.data} ({self.ora})"


class Bilet(models.Model):
    id_bilet = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    sectiune = models.CharField(max_length=10, null=True, blank=True)
    rand = models.PositiveIntegerField(null=True, blank=True)
    loc = models.PositiveIntegerField(null=True, blank=True)
    este_disponibil = models.BooleanField(default=True)
    restrictie_varsta = models.PositiveIntegerField(null=True, blank=True)
    este_returnabil = models.BooleanField(default=False)
    
    categorii = models.ManyToManyField(
        CategorieBilet, 
        related_name='bilete'
    )
    eveniment = models.ForeignKey(
        Eveniment, 
        on_delete=models.CASCADE,
        related_name='bilete'
    )
    comanda = models.ForeignKey(
        'Comanda',
        on_delete=models.SET_NULL,
        related_name='bilete',
        null=True,
        blank=True
    )

    def __str__(self):
        result = f"Bilet {self.eveniment.nume}"
        if self.sectiune or self.rand or self.loc:
            result += f": " 
        if self.sectiune:
            result += f" Sectiune {self.sectiune} "
        if self.rand:
            result += f" Rand {self.rand}"
        if self.loc:
            result += f" Loc {self.loc}"
        return result


class Utilizator(models.Model):
    TIP_CONT_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
    ]
    
    id_utilizator = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    parola = models.CharField(max_length=255)
    nume = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    tara = models.CharField(max_length=100, null=True, blank=True)
    cnp = models.CharField(max_length=13, unique=True, null=True, blank=True)
    telefon = models.CharField(max_length=20, null=True, blank=True)
    poza = models.URLField(max_length=500, null=True, blank=True)
    tip_cont = models.CharField(max_length=20, choices=TIP_CONT_CHOICES, default='BRONZE')
    
    def __str__(self):
        return self.username


class Comanda(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'În așteptare'),
        ('CONFIRMED', 'Confirmată'),
        ('DELIVERED', 'Livrată'),
        ('CANCELLED', 'Anulată'),
    ]
    
    METODA_PLATA_CHOICES = [
        ('CARD', 'Card bancar'),
        ('CASH', 'Numerar'),
        ('TRANSFER', 'Transfer bancar'),
    ]
    
    id_comanda = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_plasare = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    metoda_plata = models.CharField(max_length=20, choices=METODA_PLATA_CHOICES)
    utilizator = models.ForeignKey(
        Utilizator,
        on_delete=models.PROTECT,
        related_name='comenzi'
    )
    
    def __str__(self):
        return f"Comanda #{str(self.id_comanda)[:8]} - {self.utilizator.username}"


class Review(models.Model):
    id_review = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nota = models.PositiveIntegerField()
    mesaj = models.TextField()
    data_creare = models.DateTimeField(auto_now_add=True)
    utilizator = models.ForeignKey(
        Utilizator,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    eveniment = models.ForeignKey(
        Eveniment,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    def __str__(self):
        return f"{self.utilizator.username} - {self.eveniment.nume} ({self.nota}/10)"


class Voucher(models.Model):
    id_voucher = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    procent_reducere = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    data_expirare = models.DateTimeField()
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='vouchere'
    )
    
    def __str__(self):
        return f"Voucher {self.procent_reducere}% - Comanda #{str(self.comanda.id_comanda)[:8]}"


class Accesare:
    contor_id = 0

    def __init__(self, ip_client, url):
        Accesare.contor_id += 1
        self.id = Accesare.contor_id
        self.ip_client = ip_client
        self.url = url
        self.data = datetime.now()
        self.pagina = urlparse(url).path

    def lista_parametri(self):
        parametrii = urlparse(self.url).query
        if parametrii == "":
            return []
        lista_rezultat = list()
        for parametru in parametrii.split('&'):
            if '=' in parametru:
                lista_rezultat.append(tuple(parametru.split('=', 1)))
            else:
                lista_rezultat.append((parametru, None))
        return lista_rezultat

    def url(self):
        return self.url

    def data(self, format="%d.%m.%Y - %H:%M:%S"):
        return self.data.strftime(format)

    def pagina(self):
        return self.pagina