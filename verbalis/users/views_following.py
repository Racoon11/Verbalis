from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Following


User = get_user_model()


@login_required
def follow(request, user_id):
    followed_user = get_object_or_404(User, pk=user_id)
    Following.objects.get_or_create(
        following_user=request.user,
        followed_user=followed_user
    )
    # Безопасное получение referer
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)

    # Если referer нет — редирект на профиль
    return redirect('users:detail', pk=user_id)


@login_required
def unfollow(request, user_id):
    followed_user = get_object_or_404(User, pk=user_id)
    Following.objects.filter(
        following_user=request.user,
        followed_user=followed_user
    ).delete()
    # Безопасное получение referer
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)

    # Если referer нет — редирект на профиль
    return redirect('users:detail', pk=user_id)
