from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('info/', views.info, name='info'),
    path('despre/', views.despre, name='despre'),
    path('log/', views.log, name='log'),
    path('produse/', views.produse, name='produse'),
    path('categorii/<str:nume_categorie>/', views.categorie, name='categorie'),
    path('eveniment/<uuid:id_eveniment>/', views.eveniment_detalii, name='eveniment_detalii'),
    path('contact/', views.contact, name='contact'),
    path('inregistrare/', views.inregistrare, name='inregistrare'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profil/', views.profil, name='profil'),
    path('schimbare-parola/', views.schimbare_parola, name='schimbare_parola'),
    path('cos-virtual/', views.cos_virtual, name='cos_virtual'),
    path('sponsori/', views.sponsori, name='sponsori'),
    path('intrebari-frecvente/', views.intrebari_frecvente, name='intrebari_frecvente'),
]

