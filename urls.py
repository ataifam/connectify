from django.contrib import admin
from django.urls import include, path
from . import views

app_name = "social"
urlpatterns = [
path('logout_user', views.logout_user, name='logout'),
path('register_user', views.register_user, name='register'),
path('login_user/', views.login_user, name="login"),

path('', views.home, name="home"),
path('search', views.search, name="search"),

path('profile/<int:pk>', views.profile, name='profile'),
path('follow/<int:pk>', views.follow, name='follow'),
path('connections/', views.connections, name='connections'),

path('vote/<int:pk>', views.vote, name="vote"),
path('comment/<int:pk>', views.comment, name="comment"),

path('<int:pk>', views.updatePost, name="updatePost"),
path('<int:pk>', views.deletePost, name="deletePost"),
]