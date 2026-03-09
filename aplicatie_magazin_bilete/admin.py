from django.contrib import admin
from .models import (CategorieBilet, CategorieEveniment, Organizator, Locatie, 
                     Eveniment, Bilet, Utilizator, Comanda, Review, Voucher)


admin.site.site_header = "Panou Administrare Magazin Bilete"
admin.site.site_title = "Admin Magazin Bilete"
admin.site.index_title = "Bine ai venit în panoul de administrare!"


class CategorieBiletAdmin(admin.ModelAdmin):
    list_display = ('denumire', 'simbol', 'id')
    ordering = ('simbol',)
    search_fields = ('denumire', 'simbol')
    list_per_page = 10


class CategorieEvenimentAdmin(admin.ModelAdmin):
    list_display = ('denumire', 'culoare')
    ordering = ('denumire',)
    search_fields = ('denumire', 'descriere')
    list_per_page = 10


class OrganizatorAdmin(admin.ModelAdmin):
    list_display = ('nume', 'email')
    search_fields = ('nume', 'email')


class LocatieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'capacitate')
    search_fields = ('nume', 'capacitate')


class EvenimentAdmin(admin.ModelAdmin):
    list_display = ('nume', 'data', 'ora', 'locatie', 'organizator', 'categorie')
    list_filter = ('data', 'locatie', 'organizator', 'categorie')
    search_fields = ('nume', 'descriere')
    list_per_page = 5


class BiletAdmin(admin.ModelAdmin):
    list_display = ('eveniment', 'pret', 'sectiune', 'rand', 'loc', 'comanda')
    list_filter = ('eveniment', 'categorii', 'este_disponibil', 'este_returnabil', 'comanda')
    ordering = ('-pret',)
    search_fields = ('eveniment__nume', 'pret')
    fieldsets = (
        ('Informații Generale', {
            'fields': ('eveniment', 'categorii', 'pret', 'este_disponibil', 'este_returnabil', 'comanda')
        }),
        ('Detalii Suplimentare', {
            'fields': ('sectiune', 'rand', 'loc', 'restrictie_varsta'),
            'classes': ('collapse',),
        }),
    )


class UtilizatorAdmin(admin.ModelAdmin):
    list_display = ('username', 'nume', 'email', 'tip_cont', 'tara')
    list_filter = ('tip_cont', 'tara')
    search_fields = ('username', 'nume', 'email', 'cnp')
    ordering = ('username',)
    list_per_page = 20


class ComandaAdmin(admin.ModelAdmin):
    list_display = ('get_short_id', 'utilizator', 'data_plasare', 'status', 'metoda_plata')
    list_filter = ('status', 'metoda_plata', 'data_plasare')
    search_fields = ('utilizator__username', 'utilizator__email')
    ordering = ('-data_plasare',)
    list_per_page = 20
    
    def get_short_id(self, obj):
        return str(obj.id_comanda)[:8]
    get_short_id.short_description = 'ID Comandă'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('utilizator', 'eveniment', 'nota', 'get_short_data')
    list_filter = ('nota', 'eveniment__categorie', 'data_creare')
    search_fields = ('utilizator__username', 'eveniment__nume', 'mesaj')
    ordering = ('-data_creare',)
    list_per_page = 20
    
    def get_short_data(self, obj):
        return obj.data_creare.strftime('%Y-%m-%d %H:%M')
    get_short_data.short_description = 'Data'


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('get_short_id', 'comanda', 'procent_reducere', 'data_expirare')
    list_filter = ('data_expirare',)
    search_fields = ('comanda__utilizator__username',)
    ordering = ('-data_expirare',)
    list_per_page = 20
    
    def get_short_id(self, obj):
        return str(obj.id_voucher)[:8]
    get_short_id.short_description = 'ID Voucher'


admin.site.register(CategorieBilet, CategorieBiletAdmin)
admin.site.register(CategorieEveniment, CategorieEvenimentAdmin)
admin.site.register(Organizator, OrganizatorAdmin)
admin.site.register(Locatie, LocatieAdmin)
admin.site.register(Eveniment, EvenimentAdmin)
admin.site.register(Bilet, BiletAdmin)
admin.site.register(Utilizator, UtilizatorAdmin)
admin.site.register(Comanda, ComandaAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Voucher, VoucherAdmin)
