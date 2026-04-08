from rest_framework import serializers
from django.contrib.auth import get_user_model
from words.models import Word, Sentence, Collection
from languages.models import Language

User = get_user_model()


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'language', 'slug', 'icon']


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['id', 'sentence']


class WordSerializer(serializers.ModelSerializer):
    sentences = SentenceSerializer(many=True, read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Word
        fields = [
            'id',
            'language',
            'word',
            'word_translate',
            'part_of_speach',
            'sentences',
        ]


class CollectionSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    words = WordSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id',
            'language',
            'owner',
            'name',
            'description',
            'creation_date',
            'is_public',
            'words',
        ]


class UserSerializer(serializers.ModelSerializer):
    cur_language = LanguageSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'cur_language',
        ]
