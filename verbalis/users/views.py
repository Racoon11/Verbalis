from django.views.generic import (TemplateView, CreateView,
                                  DeleteView, UpdateView)
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Following


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
