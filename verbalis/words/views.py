# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.views.generic import ListView, CreateView, DetailView
from django.views.decorators.http import require_POST

from django.db.models import Q, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from django.http import JsonResponse

from .models import Word, UserWord, Collection, Sentence
from .forms import CollectionCreationForm, AddWordToCollectionForm


User = get_user_model()


class WordDetailView(LoginRequiredMixin, DetailView):
    model = Word
    template_name = 'words/word_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_in_userwords'] = UserWord.objects.filter(
            user=self.request.user,
            word=self.get_object()
        ).exists()
        user = self.request.user

        user_collections = Collection.objects.filter(owner=user)
        context['user_collections'] = user_collections
        context['word_collections'] = Collection.objects.filter(
            words=self.get_object())[:5].annotate(
            is_in_usercoll=Exists(
                Collection.added_users.through.objects.filter(
                    collection=OuterRef('pk'),
                    verbalisuser=user
                )
            ))
        context['sentences'] = Sentence.objects.filter(
            words=self.get_object())[:5]
        return context


# Create your views here.
class WordListView(LoginRequiredMixin, ListView):
    model = Word
    template_name = 'words/word_list.html'
    ordering = 'id'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        language = user.cur_language

        has_userword = UserWord.objects.filter(
            user=user,
            word=OuterRef('pk')
        )

        qs = Word.objects.filter(
            language=language
        ).annotate(
            is_in_userwords=Exists(has_userword)
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(word__icontains=query) |
                Q(word_translate__icontains=query)
            )

        # Возвращаем модули, упорядоченные по order
        return qs.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_collections = Collection.objects.filter(owner=self.request.user)
        context['user_collections'] = user_collections
        return context


class UserWordListView(LoginRequiredMixin, ListView):
    model = Word
    template_name = 'words/user_word_list.html'
    ordering = 'id'
    paginate_by = 12

    def get_queryset(self):
        qs = Word.objects.filter(
            userword__user=self.request.user
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(word__icontains=query) |
                Q(word_translate__icontains=query)
            )

        return qs


@login_required
def add_word_to_user(request, word_id):
    word = get_object_or_404(Word, id=word_id)

    # Проверяем, не добавлено ли уже
    if UserWord.objects.filter(user=request.user, word=word).exists():
        messages.info(request, "Это слово уже есть в вашем списке.")
    else:
        UserWord.objects.create(user=request.user, word=word)
        messages.success(request, "Слово добавлено в ваш список!")

    # Перенаправляем обратно (или на страницу слова)
    return redirect(request.META.get('HTTP_REFERER', 'words.list'))


@login_required
def add_word_from_collection_to_user(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    user = request.user

    # Получаем ID слов, которых ещё нет у пользователя
    existing_word_ids = UserWord.objects.filter(
        user=user,
        word__in=collection.words.all()
    ).values_list('word_id', flat=True)

    words_to_add = collection.words.exclude(id__in=existing_word_ids)

    # Создаём объекты UserWord
    user_words = [
        UserWord(user=user, word=word)
        for word in words_to_add
    ]

    if user_words:
        UserWord.objects.bulk_create(user_words)
    return redirect(request.META.get('HTTP_REFERER', 'word:collection_list'))


@login_required
def remove_word_to_user(request, word_id):
    word = get_object_or_404(Word, id=word_id)

    # Проверяем, не добавлено ли уже
    if not UserWord.objects.filter(user=request.user, word=word).exists():
        messages.info(request, "Это слово уже есть в вашем списке.")
    else:
        userword = UserWord.objects.get(user=request.user, word=word)
        userword.delete()

    # Перенаправляем обратно (или на страницу слова)
    return redirect(request.META.get('HTTP_REFERER', 'words.user_list'))


class CollectionListView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = 'words/collection_list.html'
    ordering = 'id'
    paginate_by = 5

    def get_queryset(self):
        # Аннотируем каждую коллекцию: добавлена ли она текущим пользователем?
        user = self.request.user
        language = user.cur_language

        qs = Collection.objects.filter(
            is_public=True,
            language=language
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        return qs.annotate(
            is_in_usercoll=Exists(
                Collection.added_users.through.objects.filter(
                    collection=OuterRef('pk'),
                    verbalisuser=user
                )
            )
        ).order_by('id')


class CollectionDetailView(LoginRequiredMixin, DetailView):
    model = Collection
    template_name = 'words/collection_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_in_usercoll'] = (self.get_object()
                                     .added_users.through.objects
                                     .filter(verbalisuser=self.request.user)
                                     .exists())
        return context


@login_required
def add_collection_to_user(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    user = request.user

    if not collection.is_public or user in collection.added_users.all():
        return redirect(request.META.get('HTTP_REFERER',
                                         'words.collection_list'))
    collection.added_users.add(user)

    # Перенаправляем обратно (или на страницу слова)
    return redirect(request.META.get('HTTP_REFERER', 'words.list'))


@login_required
def remove_collection_to_user(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    user = request.user

    if not collection.is_public or user not in collection.added_users.all():
        return redirect(request.META.get('HTTP_REFERER',
                                         'words.collection_list'))
    collection.added_users.remove(user)

    # Перенаправляем обратно (или на страницу слова)
    return redirect(request.META.get('HTTP_REFERER', 'words.list'))


class CollectionCreateView(CreateView):
    template_name = 'words/collection_form.html'
    model = Collection
    form_class = CollectionCreationForm
    success_url = reverse_lazy('words:collection_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['language'] = self.request.user.cur_language
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.language = self.request.user.cur_language
        return super().form_valid(form)


class CollectionUserListView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = 'words/collection_list.html'
    ordering = 'id'
    paginate_by = 5

    def get_queryset(self):

        user = self.request.user
        language = user.cur_language

        qs = Collection.objects.filter(
            is_public=True,
            language=language
        )

        qs = qs.filter(
            Q(added_users=self.request.user) | Q(owner=self.request.user)
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        
        return qs


@login_required
@require_POST
def add_word_to_collection(request):
    form = AddWordToCollectionForm(request.user, request.POST)
    if form.is_valid():
        collection = form.cleaned_data['collection_id']
        word = Word.objects.get(id=form.cleaned_data['word_id'])
        collection.words.add(word)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'error': 'Неверные данные'})
