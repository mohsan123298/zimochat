from django.urls import path
from . import views

app_name = 'user_auth'

urlpatterns = [
    path('', views.register, name='register'),
    path('register', views.register_post, name='register_post'),
    path('login', views.login_view, name='login'),
    path('login_post', views.login_post, name='login_post'),
    path('logout', views.user_logout, name='logout'),
    
    path('profile', views.profile, name='profile'),
    path('profile_update', views.profile_update, name='profile_update'),
]