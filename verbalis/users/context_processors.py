# users/context_processors.py
from languages.models import UserLanguageStreak
from django.utils import timezone


def user_streak(request):
    if request.user.is_authenticated and request.user.cur_language:
        streak = UserLanguageStreak.objects.filter(
            user=request.user,
            language=request.user.cur_language)
        if not streak:
            streak = UserLanguageStreak.objects.create(
                user=request.user,
                language=request.user.cur_language)
            streak.save()
        else:
            streak = streak[0]
        return {'days': streak.days,
                'streak_today':
                streak.last_updated == timezone.now().date()}
    return {'days': None}
