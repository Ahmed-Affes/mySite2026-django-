from django.contrib import admin
from .models import Donneur, Hopital, DemandeUrgente, Campagne, Don, ReponseAppel, StockSang, RendezVous, Notification, TransfertStock

admin.site.register(Donneur)
admin.site.register(Hopital)
admin.site.register(DemandeUrgente)
admin.site.register(Campagne)
admin.site.register(Don)
admin.site.register(ReponseAppel)
admin.site.register(StockSang)
admin.site.register(RendezVous)
admin.site.register(Notification)
admin.site.register(TransfertStock)
