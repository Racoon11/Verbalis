from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db import transaction
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
