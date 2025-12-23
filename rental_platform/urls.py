from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rentals import views as rentals_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/signup/', rentals_views.signup, name='signup'),
    path('accounts/login/', rentals_views.custom_login, name='login'),
    path('accounts/logout/', rentals_views.logout_view, name='logout'),
    path('', include('rentals.urls')),
]