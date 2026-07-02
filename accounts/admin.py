from django.contrib import admin
from .models import PersistentAccount, NombaAccount, Transaction

admin.site.register(PersistentAccount)
admin.site.register(NombaAccount)
admin.site.register(Transaction)