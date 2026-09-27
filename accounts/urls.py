from django.urls import path
from django.contrib.auth import views as auth_views
from .views import custom_login_view, admin_dashboard, create_user, update_user, delete_user

urlpatterns = [
    path('login/', custom_login_view, name='login'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('create_user/', create_user, name='create_user'),
    path('update_user/<int:pk>/', update_user, name='update_user'),
    path('delete_user/<int:pk>/', delete_user, name='delete_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Déconnexion avec redirection
]
