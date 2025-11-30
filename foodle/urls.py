"""
URL configuration for Foodle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from recipes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tracker/', views.tracker, name='tracker'),
    path('water-history/', views.water_history, name='water_history'),
    path('fasting-history/', views.fasting_history, name='fasting_history'),
    path('add-meal/', views.add_meal, name='add_meal'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('login/', views.LogInView.as_view(), name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('signup/', views.SignUpView.as_view(), name='sign_up'),
    path('feed/', views.feed, name='feed'),
    path('recipes/', views.recipes, name='recipes'),

    #Password Reset URLs
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='recipes/auth/password_reset.html'
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='recipes/auth/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='recipes/auth/password_reset_confirm.html'
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='recipes/auth/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
