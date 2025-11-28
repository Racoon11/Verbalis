from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .models import UserLanguageStreak


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
