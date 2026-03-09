from django import forms
from django.core.exceptions import ValidationError
from .models import CategorieEveniment, Organizator, Locatie, Utilizator
from datetime import date, datetime
import re



class FiltruProduseForm(forms.Form):
    nume = forms.CharField(
        required=False,
        label='Nume eveniment',
        widget=forms.TextInput(attrs={
            'placeholder': 'Caută după nume...',
            'class': 'form-control'
        })
    )
    data_min = forms.DateField(
        required=False,
        label='Dată de la',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    data_max = forms.DateField(
        required=False,
        label='Dată până la',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    ora_min = forms.TimeField(
        required=False,
        label='Oră de la',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    ora_max = forms.TimeField(
        required=False,
        label='Oră până la',
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        })
    )
    durata_min_h = forms.IntegerField(
        required=False,
        label='Durată minimă (ore)',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min ore',
            'class': 'form-control'
        })
    )
    durata_max_h = forms.IntegerField(
        required=False,
        label='Durată maximă (ore)',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max ore',
            'class': 'form-control'
        })
    )
    categorie = forms.ModelChoiceField(
        required=False,
        label='Categorie',
        queryset=CategorieEveniment.objects.all().order_by('denumire'),
        empty_label='Toate categoriile',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    organizator = forms.ModelChoiceField(
        required=False,
        label='Organizator',
        queryset=Organizator.objects.all().order_by('nume'),
        empty_label='Toți organizatorii',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    locatie = forms.ModelChoiceField(
        required=False,
        label='Locație',
        queryset=Locatie.objects.all().order_by('nume'),
        empty_label='Toate locațiile',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    capacitate_min = forms.IntegerField(
        required=False,
        label='Capacitate minimă',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min capacitate',
            'class': 'form-control'
        })
    )
    capacitate_max = forms.IntegerField(
        required=False,
        label='Capacitate maximă',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max capacitate',
            'class': 'form-control'
        })
    )
    elemente_per_pagina = forms.IntegerField(
        required=False,
        label='Elemente per pagină',
        min_value=1,
        max_value=100,
        initial=9,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Nr. evenimente',
            'class': 'form-control',
            'value': '9'
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        data_min = cleaned_data.get('data_min')
        data_max = cleaned_data.get('data_max')
        if data_min and data_max and data_max < data_min:
            raise forms.ValidationError(
                'Data de început trebuie să fie înainte de sau identică cu data de final!'
            )
        ora_min = cleaned_data.get('ora_min')
        ora_max = cleaned_data.get('ora_max')
        if ora_min and ora_max and ora_max <= ora_min:
            raise forms.ValidationError(
                'Ora de început trebuie să fie înainte de sau identică cu ora de final!'
            )
        durata_min_h = cleaned_data.get('durata_min_h')
        durata_max_h = cleaned_data.get('durata_max_h')
        if durata_min_h is not None and durata_max_h is not None and durata_max_h < durata_min_h:
            raise forms.ValidationError(
                'Durata minimă trebuie să fie mai mică sau egală decât durata maximă!'
            )
        capacitate_min = cleaned_data.get('capacitate_min')
        capacitate_max = cleaned_data.get('capacitate_max')
        if capacitate_min is not None and capacitate_max is not None and capacitate_max < capacitate_min:
            raise forms.ValidationError(
                'Capacitatea minimă trebuie să fie mai mică sau egală decât capacitatea maximă!'
            )
        return cleaned_data

class ContactForm(forms.Form):
    TIPURI_MESAJ = [
        ('neselectat', 'Neselectat'),
        ('reclamatie', 'Reclamație'),
        ('intrebare', 'Întrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]

    def validare_varsta(self, value):
        if not value:
            return
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValidationError(
                'Trebuie să aveți cel puțin 18 ani pentru a trimite un mesaj.',
                code='underage'
            )

    def validare_numar_cuvinte(self, value):
        if not value:
            return
        words = re.findall(r'\w+', value)
        word_count = len(words)
        if word_count < 5 or word_count > 100:
            raise ValidationError(
                f'Mesajul trebuie să conțină între 5 și 100 de cuvinte. Aveți {word_count} cuvinte.',
                code='invalid_word_count'
            )

    def validare_lungime_maxima(self, value):
        if not value:
            return
        words = re.findall(r'\w+', value)
        for word in words:
            if len(word) > 15:
                raise ValidationError(
                    f'Cuvântul "{word}" depășește lungimea maximă de 15 caractere.',
                    code='word_too_long'
                )

    def validate_no_links(self, value):
        if not value:
            return
        if 'http://' in value.lower() or 'https://' in value.lower():
            raise ValidationError(
                'Câmpul nu poate conține linkuri (http:// sau https://).',
                code='contains_links'
            )

    def validate_cnp_digits(self, value):
        if not value:
            return
        if not value.isdigit():
            raise ValidationError(
                'CNP-ul trebuie să conțină doar cifre.',
                code='cnp_not_digits'
            )

    def validare_cnp_format(self, value):
        if not value or len(value) != 13:
            return
        first_digit = value[0]
        if first_digit not in ['1', '2', '5', '6']:
            raise ValidationError(
                'CNP-ul trebuie să înceapă cu 1, 2, 5 sau 6.',
                code='invalid_cnp_start'
            )
        year_digits = value[1:3]
        month_digits = value[3:5]
        day_digits = value[5:7]
        try:
            year = int(year_digits)
            month = int(month_digits)
            day = int(day_digits)
            if first_digit in ['1', '2']:
                year += 1900
            elif first_digit in ['5', '6']:
                year += 2000
            datetime(year, month, day)
        except ValueError:
            raise ValidationError(
                f'Data din CNP ({day_digits}/{month_digits}/{year_digits}) nu este validă.',
                code='invalid_cnp_date'
            )

    def validate_no_temp_email(self, value):
        if not value:
            return
        temp_domains = ['guerillamail.com', 'yopmail.com']
        email_lower = value.lower()
        for domain in temp_domains:
            if domain in email_lower:
                raise ValidationError(
                    'Nu sunt acceptate adrese de email temporare.',
                    code='temp_email'
                )

    def validate_text_format(self, value):
        if not value:
            return
        if not value[0].isupper() or not value[0].isalpha():
            raise ValidationError(
                'Câmpul trebuie să înceapă cu literă mare.',
                code='no_capital_start'
            )
        if not re.match(r'^[a-zA-ZăâîșțĂÂÎȘȚ\s\-]+$', value):
            raise ValidationError(
                'Câmpul trebuie să conțină doar litere, spații și cratimă.',
                code='invalid_characters'
            )

    def validate_capital_after_separator(self, value):
        if not value:
            return
        for i, char in enumerate(value):
            if char in [' ', '-']:
                if i + 1 < len(value):
                    next_char = value[i + 1]
                    if next_char.isalpha() and not next_char.isupper():
                        raise ValidationError(
                            'După spațiu sau cratimă trebuie să urmeze literă mare.',
                            code='no_capital_after_separator'
                        )
    
    nume = forms.CharField(
        required=True,
        max_length=10,
        label='Nume',
        widget=forms.TextInput(attrs={
            'placeholder': 'Numele dumneavoastră',
            'class': 'form-control'
        })
    )
    prenume = forms.CharField(
        required=False,
        max_length=10,
        label='Prenume',
        widget=forms.TextInput(attrs={
            'placeholder': 'Prenumele dumneavoastră (opțional)',
            'class': 'form-control'
        })
    )
    cnp = forms.CharField(
        required=False,
        min_length=13,
        max_length=13,
        label='CNP',
        widget=forms.TextInput(attrs={
            'placeholder': '13 caractere (opțional)',
            'class': 'form-control'
        })
    )
    data_nasterii = forms.DateField(
        required=True,
        label='Data nașterii',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'adresa@email.com',
            'class': 'form-control'
        })
    )
    confirmare_email = forms.EmailField(
        required=True,
        label='Confirmare e-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Confirmați adresa de email',
            'class': 'form-control'
        })
    )
    tip_mesaj = forms.ChoiceField(
        required=True,
        choices=TIPURI_MESAJ,
        initial='neselectat',
        label='Tip mesaj',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    subiect = forms.CharField(
        required=True,
        max_length=100,
        label='Subiect',
        widget=forms.TextInput(attrs={
            'placeholder': 'Subiectul mesajului',
            'class': 'form-control'
        })
    )
    minim_zile_asteptare = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=30,
        label='Minim zile așteptare',
        help_text='Pentru review-uri/cereri minimul de zile de așteptare trebuie setat de la 4 încolo iar pentru cereri/întrebări de la 2 încolo. Maximul e 30.',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Număr zile (1-30)',
            'class': 'form-control'
        })
    )
    mesaj = forms.CharField(
        required=True,
        label='Mesaj (vă rugăm să vă semnați)',
        widget=forms.Textarea(attrs={
            'placeholder': 'Scrie-ți mesajul aici și semnează-te...',
            'class': 'form-control',
            'rows': 5
        })
    )
    
    def clean_nume(self):
        nume = self.cleaned_data.get('nume')
        if nume:
            self.validate_text_format(nume)
            self.validate_capital_after_separator(nume)
        return nume
    
    def clean_prenume(self):
        prenume = self.cleaned_data.get('prenume')
        if prenume:
            self.validate_text_format(prenume)
            self.validate_capital_after_separator(prenume)
        return prenume
    
    def clean_cnp(self):
        cnp = self.cleaned_data.get('cnp')
        if cnp:
            self.validate_cnp_digits(cnp)
            self.validare_cnp_format(cnp)
        return cnp
    
    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if data_nasterii:
            self.validare_varsta(data_nasterii)
        return data_nasterii
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            self.validate_no_temp_email(email)
        return email
    
    def clean_tip_mesaj(self):
        tip_mesaj = self.cleaned_data.get('tip_mesaj')
        if tip_mesaj == 'neselectat':
            raise ValidationError(
                'Trebuie să selectați un tip de mesaj valid.',
                code='invalid_message_type'
            )
        return tip_mesaj
    
    def clean_subiect(self):
        subiect = self.cleaned_data.get('subiect')
        if subiect:
            self.validate_text_format(subiect)
            self.validate_no_links(subiect)
        return subiect
    
    def clean_mesaj(self):
        mesaj = self.cleaned_data.get('mesaj')
        if mesaj:
            self.validare_numar_cuvinte(mesaj)
            self.validare_lungime_maxima(mesaj)
            self.validate_no_links(mesaj)
        return mesaj
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirmare_email = cleaned_data.get('confirmare_email')
        if email and confirmare_email and email != confirmare_email:
            raise forms.ValidationError(
                'Adresa de e-mail și confirmarea e-mail-ului nu coincid!'
            )
        tip_mesaj = cleaned_data.get('tip_mesaj')
        minim_zile_asteptare = cleaned_data.get('minim_zile_asteptare')
        if tip_mesaj and minim_zile_asteptare is not None:
            if tip_mesaj in ['review', 'cerere'] and minim_zile_asteptare < 4:
                raise forms.ValidationError(
                    f'Pentru {tip_mesaj}, minimul de zile de așteptare trebuie să fie de la 4 încolo!'
                )
            elif tip_mesaj in ['intrebare'] and minim_zile_asteptare < 2:
                raise forms.ValidationError(
                    f'Pentru {tip_mesaj}, minimul de zile de așteptare trebuie să fie de la 2 încolo!'
                )
        nume = cleaned_data.get('nume')
        mesaj = cleaned_data.get('mesaj')
        if nume and mesaj:
            words = re.findall(r'\w+', mesaj)
            if words:
                last_word = words[-1]
                if last_word.lower() != nume.lower():
                    raise forms.ValidationError(
                        f'Mesajul trebuie să se termine cu semnătura dumneavoastră (numele "{nume}"). Ultimul cuvânt este "{last_word}".',
                        code='missing_signature'
                    )
        cnp = cleaned_data.get('cnp')
        data_nasterii = cleaned_data.get('data_nasterii')
        if cnp and data_nasterii and len(cnp) == 13:
            sex_digit = cnp[0]
            cnp_year_digits = cnp[1:3]
            cnp_month = cnp[3:5]
            cnp_day = cnp[5:7]
            if sex_digit in ['1', '2']:
                cnp_year = 1900 + int(cnp_year_digits)
            elif sex_digit in ['5', '6']:
                cnp_year = 2000 + int(cnp_year_digits)
            else:
                cnp_year = None
            if cnp_year:
                if (cnp_year != data_nasterii.year or 
                    int(cnp_month) != data_nasterii.month or 
                    int(cnp_day) != data_nasterii.day):
                    raise forms.ValidationError(
                        f'Data din CNP ({cnp_day}/{cnp_month}/{cnp_year}) nu corespunde cu data nașterii ({data_nasterii.day:02d}/{data_nasterii.month:02d}/{data_nasterii.year}).',
                        code='cnp_date_mismatch'
                    )
        return cleaned_data

class InregistrareForm(forms.Form):
    VALID_COUNTRIES = [
        'România', 'Republica Moldova', 'Ungaria', 'Bulgaria',
        'Ucraina', 'Serbia', 'Germania', 'Franța', 'Italia',
        'Spania', 'Marea Britanie', 'Belgia', 'Olanda',
        'Portugalia', 'Austria', 'Elveția', 'Polonia',
        'Cehia', 'Slovacia', 'Grecia', 'Turcia',
        'SUA', 'Canada', 'Australia', 'Japonia', 'China'
    ]

    username = forms.CharField(
        required=True,
        max_length=50,
        label='Nume utilizator',
        widget=forms.TextInput(attrs={
            'placeholder': 'Alegeți un nume de utilizator unic',
            'class': 'form-control'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'adresa@email.com',
            'class': 'form-control'
        })
    )
    
    parola = forms.CharField(
        required=True,
        max_length=255,
        label='Parolă',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Introduceți parola',
            'class': 'form-control'
        })
    )
    
    confirmare_parola = forms.CharField(
        required=True,
        max_length=255,
        label='Confirmare parolă',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmați parola',
            'class': 'form-control'
        })
    )
    
    nume = forms.CharField(
        required=True,
        max_length=200,
        label='Nume complet',
        widget=forms.TextInput(attrs={
            'placeholder': 'Numele dumneavoastră complet',
            'class': 'form-control'
        })
    )
    
    tip_cont = forms.ChoiceField(
        required=True,
        choices=Utilizator.TIP_CONT_CHOICES,
        initial='BRONZE',
        label='Tip cont',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tara = forms.ChoiceField(
        required=False,
        choices=[('', '--- Selectați țara ---')] + [(c, c) for c in VALID_COUNTRIES],
        label='Țara',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    cnp = forms.CharField(
        required=False,
        max_length=13,
        label='CNP (opțional)',
        widget=forms.TextInput(attrs={
            'placeholder': '13 cifre (opțional)',
            'class': 'form-control'
        })
    )
    
    telefon = forms.CharField(
        required=False,
        max_length=20,
        label='Telefon (opțional)',
        widget=forms.TextInput(attrs={
            'placeholder': '+40712345678 sau 0712345678',
            'class': 'form-control'
        })
    )
    
    poza = forms.URLField(
        required=False,
        max_length=500,
        label='URL poză profil (opțional)',
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/avatar.jpg',
            'class': 'form-control'
        })
    )

    def validate_cnp_inregistrare(self, value):
        if not value:
            return
        if len(value) != 13:
            raise ValidationError(
                'CNP-ul trebuie să aibă exact 13 cifre.',
                code='cnp_invalid_length'
            )
        if not value.isdigit():
            raise ValidationError(
                'CNP-ul trebuie să conțină doar cifre.',
                code='cnp_not_digits'
            )
        sex_digit = value[0]
        if sex_digit not in ['1', '2', '5', '6', '7', '8']:
            raise ValidationError(
                'CNP-ul trebuie să înceapă cu 1, 2, 5, 6, 7 sau 8.',
                code='invalid_cnp_start'
            )
        year_digits = value[1:3]
        month_digits = value[3:5]
        day_digits = value[5:7]
        try:
            year = int(year_digits)
            month = int(month_digits)
            day = int(day_digits)
            if sex_digit in ['1', '2']:
                year += 1900
            elif sex_digit in ['5', '6']:
                year += 2000
            elif sex_digit in ['7', '8']:
                year += 1800
            datetime(year, month, day)
        except ValueError:
            raise ValidationError(
                f'Data din CNP ({day_digits}/{month_digits}/{year_digits}) nu este validă.',
                code='invalid_cnp_date'
            )
        control_key = '279146358279'
        suma = sum(int(value[i]) * int(control_key[i]) for i in range(12))
        rest = suma % 11
        control_digit = rest if rest < 10 else 1
        if int(value[12]) != control_digit:
            raise ValidationError(
                'Cifra de control a CNP-ului este invalidă.',
                code='invalid_cnp_control'
            )

    def validate_telefon_romania(self, value):
        if not value:
            return
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        if cleaned.startswith('+40'):
            if len(cleaned) != 12:
                raise ValidationError(
                    'Numărul de telefon în format +40 trebuie să aibă 12 caractere (+40XXXXXXXXX).',
                    code='invalid_phone_length'
                )
            if not cleaned[1:].isdigit():
                raise ValidationError(
                    'Numărul de telefon trebuie să conțină doar cifre după +.',
                    code='phone_not_digits'
                )
            if not cleaned.startswith('+407'):
                raise ValidationError(
                    'Numărul de telefon românesc trebuie să înceapă cu +407.',
                    code='invalid_phone_prefix'
                )
        elif cleaned.startswith('07'):
            if len(cleaned) != 10:
                raise ValidationError(
                    'Numărul de telefon în format 07 trebuie să aibă 10 cifre (07XXXXXXXX).',
                    code='invalid_phone_length'
                )
            if not cleaned.isdigit():
                raise ValidationError(
                    'Numărul de telefon trebuie să conțină doar cifre.',
                    code='phone_not_digits'
                )
        else:
            raise ValidationError(
                'Numărul de telefon trebuie să înceapă cu +40 sau 07.',
                code='invalid_phone_format'
            )

    def validate_tara_lista(self, value):
        if not value:
            return
        VALID_COUNTRIES = [
            'România', 'Republica Moldova', 'Ungaria', 'Bulgaria',
            'Ucraina', 'Serbia', 'Germania', 'Franța', 'Italia',
            'Spania', 'Marea Britanie', 'Belgia', 'Olanda',
            'Portugalia', 'Austria', 'Elveția', 'Polonia',
            'Cehia', 'Slovacia', 'Grecia', 'Turcia',
            'SUA', 'Canada', 'Australia', 'Japonia', 'China'
        ]
        if value not in VALID_COUNTRIES:
            raise ValidationError(
                f'Țara "{value}" nu este în lista țărilor acceptate. Alegeți din listă.',
                code='invalid_country'
            )

    def validate_url_imagine_extensie(self, value):
        if not value:
            return
        VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        value_lower = value.lower()
        has_valid_extension = any(value_lower.endswith(ext) for ext in VALID_EXTENSIONS)
        if not has_valid_extension:
            raise ValidationError(
                f'URL-ul imaginii trebuie să se termine cu una din extensiile: {", ".join(VALID_EXTENSIONS)}',
                code='invalid_image_extension'
            )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if Utilizator.objects.filter(username=username).exists():
                raise ValidationError(
                    f'Numele de utilizator "{username}" este deja folosit. Alegeți un altul.',
                    code='username_exists'
                )
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if Utilizator.objects.filter(email=email).exists():
                raise ValidationError(
                    f'Adresa de email "{email}" este deja înregistrată.',
                    code='email_exists'
                )
        return email
    
    def clean_cnp(self):
        cnp = self.cleaned_data.get('cnp')
        if cnp:
            self.validate_cnp_inregistrare(cnp)
            if Utilizator.objects.filter(cnp=cnp).exists():
                raise ValidationError(
                    'Acest CNP este deja înregistrat în sistem.',
                    code='cnp_exists'
                )
        return cnp

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if telefon:
            self.validate_telefon_romania(telefon)
        return telefon
    
    def clean_tara(self):
        tara = self.cleaned_data.get('tara')
        if tara:
            self.validate_tara_lista(tara)
        return tara
    
    def clean_poza(self):
        poza = self.cleaned_data.get('poza')
        if poza:
            self.validate_url_imagine_extensie(poza)
        return poza
    
    def clean(self):
        cleaned_data = super().clean()
        parola = cleaned_data.get('parola')
        confirmare_parola = cleaned_data.get('confirmare_parola')
        if parola and confirmare_parola:
            if parola != confirmare_parola:
                raise forms.ValidationError(
                    'Parolele nu coincid! Vă rugăm să introduceți aceeași parolă în ambele câmpuri.',
                    code='password_mismatch'
                )
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=50,
        label='Nume utilizator sau Email',
        widget=forms.TextInput(attrs={
            'placeholder': 'Introduceți username sau email',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    parola = forms.CharField(
        required=True,
        max_length=255,
        label='Parolă',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Introduceți parola',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label='Ține-mă minte (timp de o zi)',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class SchimbareParolaForm(forms.Form):
    parola_veche = forms.CharField(
        required=True,
        max_length=255,
        label='Parola actuală',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Introduceți parola actuală',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    parola_noua = forms.CharField(
        required=True,
        max_length=255,
        label='Parolă nouă',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Introduceți parola nouă',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    confirmare_parola_noua = forms.CharField(
        required=True,
        max_length=255,
        label='Confirmă parola nouă',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmați parola nouă',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        parola_noua = cleaned_data.get('parola_noua')
        confirmare_parola_noua = cleaned_data.get('confirmare_parola_noua')
        if parola_noua and confirmare_parola_noua:
            if parola_noua != confirmare_parola_noua:
                raise forms.ValidationError(
                    'Parolele noi nu coincid! Vă rugăm să introduceți aceeași parolă în ambele câmpuri.',
                    code='password_mismatch'
                )
        return cleaned_data
