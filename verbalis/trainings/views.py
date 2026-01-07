from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db import transaction
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

import json
import random

from words.models import Word
from .models import UserLanguageTraining, TrainingModule


class TrainingListView(LoginRequiredMixin, ListView):
    model = TrainingModule
    template_name = 'trainings/training_list.html'
    context_object_name = 'modules'

    def get_queryset(self):
        user = self.request.user
        language = user.cur_language

        # Проверяем, есть ли уже записи для этого языка
        if not UserLanguageTraining.objects.filter(
            user=user,
            language=language
        ).exists():
            # Если нет — создаём базовые записи
            self._initialize_user_training(user, language)

        # Возвращаем модули, упорядоченные по order
        return TrainingModule.objects.filter(
            userlanguagetraining__user=user,
            userlanguagetraining__language_id=language
        ).order_by('userlanguagetraining__order')

    def _initialize_user_training(self, user, language):
        """
        Создаёт базовые записи UserLanguageTraining для пользователя и языка.
        Берёт все существующие TrainingModule и назначает их с order = id.
        """
        with transaction.atomic():
            # Получаем все модули (предполагается, что они "базовые")
            all_modules = TrainingModule.objects.filter(
                base_order__isnull=False).order_by('base_order')
            UserLanguageTraining.objects.bulk_create([
                UserLanguageTraining(
                    user=user,
                    language=language,
                    training=module,
                    order=module.base_order
                )
                for module in all_modules
            ])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TrainingEditListView(LoginRequiredMixin, ListView):
    model = TrainingModule
    template_name = 'trainings/edit.html'
    context_object_name = 'modules'

    def get_queryset(self):
        user = self.request.user
        language = user.cur_language

        return TrainingModule.objects.filter(
            userlanguagetraining__user=user,
            userlanguagetraining__language_id=language
        ).order_by('userlanguagetraining__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def training_view(request):
    today = timezone.now().date()
    user = request.user
    words = Word.objects.filter(
        userword__user=user,
        userword__next_train_date__lte=today
    )[:5]

    # Префетчим предложения, чтобы избежать N+1
    words_with_sents = words.prefetch_related('sentences')
    words_data = []
    for word in words_with_sents:
        # Преобразуем QuerySet предложений в список словарей
        sentences_list = [
            {
                'text': sent.sentence,
            }
            for sent in word.sentences.all()[:5]
        ]

        words_data.append({
            'id': word.id,
            'word': word.word,
            'translation': word.word_translate,
            'part_of_speach': word.part_of_speach,
            'sentences': sentences_list  # ← теперь это обычный список!
        })

    context = {
        'words': json.dumps(words_data, ensure_ascii=False),
        'user_id': user.id
    }
    return render(request, 'trainings/train.html', context)


def get_similar(request, pk):
    word = get_object_or_404(Word, pk=pk)
    lang = word.language
    words = Word.objects.exclude(pk=pk).filter(language=lang)

    word_ids = words.values_list('id', flat=True)
    random_ids = random.sample(list(word_ids), 3)
    words = Word.objects.filter(id__in=random_ids)

    words_data = [
        {
            'id': word.id,
            'word': word.word,
            'translation': word.word_translate,
            # добавь другие поля, которые нужны
        }
        for word in words
    ]
    return JsonResponse({'words': words_data})
