from django.urls import path
from . import views


app_name = 'trainings'
urlpatterns = [
    path('', views.TrainingListView.as_view(),
         name='list'),
    path('edit/', views.TrainingEditListView.as_view(), name='edit'),
    path('train/', views.training_view, name='train'),
    path('get-similar/<int:pk>/',
         views.get_similar, name='get-similar'),
]
