from django.contrib import admin

from .models import Word, Sentence, Collection

admin.site.register([Word, Sentence, Collection])
