from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import VerbalisUser


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('cur_language',)}),
)
# Регистрируем модель в админке:
admin.site.register(VerbalisUser, UserAdmin)
