from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import UserLanguageStreak, Language


# Create your views here.
@login_required
def increment_streak(request, language_code):
    if request.method != 'POST':
        return HttpResponseForbidden("Only POST allowed")

    # Находим или создаём запись
    streak, created = UserLanguageStreak.objects.get_or_create(
        user=request.user,
        language=language_code
    )
    if streak.can_increment():
        streak.days += 1
        streak.save()

    # Перенаправляем на ту же страницу (или куда нужно)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def switch_language(request, language_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Only POST allowed")
    language = get_object_or_404(Language, id=language_id)
    # Переключаем только если у пользователя есть streak для этого языка
    get_object_or_404(UserLanguageStreak, user=request.user, language=language)
    request.user.cur_language = language
    request.user.save(update_fields=['cur_language'])
    return redirect(request.META.get('HTTP_REFERER', '/'))
