from rest_framework import viewsets, permissions, filters
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response

from words.models import Word, Collection
from languages.models import Language

from .serializers import (
    WordSerializer,
    LanguageSerializer,
    CollectionSerializer,
    UserSerializer,
)

User = get_user_model()


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Word.objects.select_related('language')
        .prefetch_related('sentences')
        .all()
    )
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['word', 'word_translate']

    def get_queryset(self):
        qs = super().get_queryset()
        lang = self.request.query_params.get('language')
        if lang:
            # allow passing id or slug
            if lang.isdigit():
                qs = qs.filter(language__id=int(lang))
            else:
                qs = qs.filter(language__slug=lang)
        return qs


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Collection.objects.select_related('language', 'owner')
        .prefetch_related('words')
        .all()
    )
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
