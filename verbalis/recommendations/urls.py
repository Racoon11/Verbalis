from django.urls import path
from . import views


app_name = 'recsys'
urlpatterns = [
    path('', views.RandomWordListView.as_view(), name='test'),
    path('get-recs', views.get_recommendations, name='recs'),
    path('save-recs', views.save_results, name='save'),
]
