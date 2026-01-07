from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

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


class FollowersListView(LoginRequiredMixin, ListView):
    model = User
    ordering = 'id'
    paginate_by = 5
    context_object_name = 'users'
    template = 'users/verbalisuser_list.html'

    def get_queryset(self):
        target_user = get_object_or_404(User, pk=self.kwargs['pk'])

        qs = User.objects.filter(
            following_set__followed_user=target_user
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )

        return qs


class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    ordering = 'id'
    paginate_by = 5
    context_object_name = 'users'
    template = 'users/verbalisuser_list.html'

    def get_queryset(self):
        target_user = get_object_or_404(User, pk=self.kwargs['pk'])
        qs = User.objects.filter(
            followers_set__following_user=target_user
        )

        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )

        return qs
