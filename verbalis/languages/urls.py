from django.urls import path
from . import views


app_name = 'languages'
urlpatterns = [
    path('<str:language_code>/add/', views.increment_streak,
         name='increment_streak'),
    path('<int:language_id>/switch/', views.switch_language,
         name='switch_language'),
]
