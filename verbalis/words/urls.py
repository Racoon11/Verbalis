from django.urls import path
from . import views


app_name = 'words'
urlpatterns = [
    path('list/', views.WordListView.as_view(), name='list'),
    path('my_words/', views.UserWordListView.as_view(), name='user_list'),
    path('add-word/<int:word_id>/', views.add_word_to_user, name='add_word'),
    path('remove-word/<int:word_id>/',
         views.remove_word_to_user, name='remove_word'),
]
