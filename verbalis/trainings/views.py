from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db import transaction
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

import json
import random
from datetime import timedelta

from words.models import Word, UserWord
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
        context['words_to_repeat'] = UserWord.objects.filter(
            user=self.request.user,
            train_number__gt=0,
            next_train_date__lte=timezone.now().date()
            ).count()
        context['new_words'] = UserWord.objects.filter(
            user=self.request.user,
            train_number=0,
            next_train_date__lte=timezone.now().date()).count()
        return context


@login_required
def training_edit_view(request):
    user = request.user
    language = user.cur_language

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        module_ids = data.get('modules', [])
        with transaction.atomic():
            UserLanguageTraining.objects.filter(
                user=user, language=language
            ).delete()
            UserLanguageTraining.objects.bulk_create([
                UserLanguageTraining(
                    user=user,
                    language=language,
                    training_id=module_id,
                    order=idx + 1,
                )
                for idx, module_id in enumerate(module_ids)
            ])
        return JsonResponse({'status': 'ok'})

    user_modules = TrainingModule.objects.filter(
        userlanguagetraining__user=user,
        userlanguagetraining__language=language,
    ).order_by('userlanguagetraining__order')

    user_module_ids = set(user_modules.values_list('id', flat=True))
    available_modules = TrainingModule.objects.exclude(id__in=user_module_ids)

    return render(request, 'trainings/edit.html', {
        'user_modules': user_modules,
        'available_modules': available_modules,
    })


@login_required
def training_view(request):
    today = timezone.now().date()
    user = request.user
    words = Word.objects.filter(
        userword__user=user,
        userword__next_train_date__lte=today
    )[:5]
    train_order = list(UserLanguageTraining.objects.filter(
        user=user, language=user.cur_language
    ).order_by('order').values_list('training_id', flat=True))

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
        'order': train_order,
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


@login_required
def update_word_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        ids = data.get('wordIds')
        mistakes = data.get('mistakes')
        user = request.user
        today = timezone.now().date()

        objects = UserWord.objects.filter(
            user=user,
            word_id__in=ids
        )

        next_train_dates = [1, 3, 7, 30, 60]
        for w in range(len(objects)):
            if mistakes[w] == 0:
                objects[w].next_train_date = today + timedelta(
                    days=next_train_dates[objects[w].train_number])
                objects[w].train_number += 1
            else:
                objects[w].next_train_date = today + timedelta(days=1)
            objects[w].save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)
