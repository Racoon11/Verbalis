from django.urls import path
from . import views, views_following

app_name = 'users'
urlpatterns = [
    path('', views.AboutPage.as_view(), name='about'),
    path('auth/registration/', views.UserCreateView.as_view(),
         name='registration'),

    path('profile/<int:pk>/', views.UserDetailView.as_view(),
         name='detail'),
    path('profile/<int:pk>/followers/',
         views_following.FollowersListView.as_view(), name='followers'),
    path('profile/<int:pk>/following/',
         views_following.FollowingListView.as_view(), name='following'),
    path('profile/edit/', views.UserUpdateView.as_view(), name='edit'),
    path('profile/list/', views.UserListView.as_view(), name='list'),

    path('follow/<int:user_id>/', views_following.follow, name='follow'),
    path('unfollow/<int:user_id>/', views_following.unfollow, name='unfollow'),
]
