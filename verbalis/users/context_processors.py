# users/context_processors.py
from languages.models import UserLanguageStreak
from words.models import UserWord
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
        today = timezone.now().date()
        words = UserWord.objects.filter(
            user=request.user,
            next_train_date__lte=today,
            word__language=request.user.cur_language
        ).count()
        return {'days': streak.days,
                'streak_today':
                streak.last_updated == today,
                'words_count': words}
    return {'days': None}
