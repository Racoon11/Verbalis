from rest_framework import serializers
from .models import Word


class WordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Word
        fields = ('id', 'word', 'word_translate', 'part_of_speach')
