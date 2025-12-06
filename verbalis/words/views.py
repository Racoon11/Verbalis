# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.views.generic import ListView
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect

from .models import Word, UserWord


User = get_user_model()


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


class UserWordListView(LoginRequiredMixin, ListView):
    model = Word
    template_name = 'words/user_word_list.html'
    ordering = 'id'
    paginate_by = 12

    def get_queryset(self):
        return Word.objects.filter(
            userword__user=self.request.user
        ).order_by('id')


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
