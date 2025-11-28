from django.views.generic import (TemplateView, CreateView,
                                  DeleteView, UpdateView, ListView)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Following
from .forms import CustomUserCreationForm, CustomUserUpdateForm


User = get_user_model()


class AboutPage(TemplateView):
    template_name = 'users/about.html'


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:about')


class UserDetailView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        user = self.request.user

        context['is_following'] = Following.objects.filter(
            following_user=user,
            followed_user=profile_user
        ).exists()

        context['number_following'] = Following.objects.filter(
            followed_user=profile_user).count()
        context['number_followed'] = Following.objects.filter(
            following_user=profile_user).count()

        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'registration/edit_form.html'
    form_class = CustomUserUpdateForm
    # success_url = reverse_lazy('users:detail')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:detail', kwargs={'pk': self.object.pk})


class UserListView(LoginRequiredMixin, ListView):
    model = User
    ordering = 'id'
    paginate_by = 5
    context_object_name = 'users'

    def get_queryset(self):
        # Базовый queryset: все пользователи, кроме текущего и подписанных
        following_ids = Following.objects.filter(
            following_user=self.request.user
        ).values_list('followed_user_id', flat=True)

        qs = User.objects.exclude(
            id__in=list(following_ids) + [self.request.user.id]
        )

        # Получаем поисковый запрос из GET-параметра `q`
        query = self.request.GET.get('q', '').strip()

        if query:
            # Фильтруем по username, first_name, last_name
            qs = qs.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )

        return qs.order_by('id')
