from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.AboutPage.as_view(), name='about'),
    path('auth/registration/', views.UserCreateView.as_view(),
         name='registration'),
]
