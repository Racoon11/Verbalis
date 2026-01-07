from django.urls import path
from . import views


app_name = 'words'
urlpatterns = [
    path('word/<int:pk>/', views.WordDetailView.as_view(), name='detail'),
    path('list/', views.WordListView.as_view(), name='list'),
    path('my_words/', views.UserWordListView.as_view(), name='user_list'),
    path('add-word/<int:word_id>/', views.add_word_to_user, name='add_word'),
    path('remove-word/<int:word_id>/',
         views.remove_word_to_user, name='remove_word'),

    path('collection/<int:pk>/',
         views.CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/list/',
         views.CollectionListView.as_view(), name='collection_list'),
    path('collection/add-collection/<int:collection_id>/',
         views.add_collection_to_user, name='add_collection'),
    path('collection/remove-collection/<int:collection_id>/',
         views.remove_collection_to_user, name='remove_collection'),
    path('collection/create/',
         views.CollectionCreateView.as_view(), name='create_collection'),
    path('collection/my-list/',
         views.CollectionUserListView.as_view(), name='user_collection_list'),
    path('add-word-to-collection/',
         views.add_word_to_collection, name='add_word_to_collection'),
    path('collection/add_all_words/<int:collection_id>/',
         views.add_word_from_collection_to_user,
         name='add_all_words_collection'),

]
