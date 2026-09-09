from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, ProfileView, admin_logout, admin_login

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path("admin-login/", admin_login, name="admin_login"),
    path("admin-logout/", admin_logout, name="admin_logout")        
]
