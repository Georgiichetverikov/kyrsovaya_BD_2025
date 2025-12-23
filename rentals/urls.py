from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('items/<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('items/<int:item_id>/rent/', views.create_rental_request, name='create_rental_request'),
    path('users/<int:user_id>/rating/', views.user_rating, name='user_rating'),
    path('users/<int:user_id>/', views.user_profile, name='user_profile'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    path('me/', views.user_dashboard, name='user_dashboard'),
    path('me/items/', views.my_items, name='my_items'),
    path('me/rentals/', views.my_rentals, name='my_rentals'),
    path('me/requests/', views.owner_requests, name='owner_requests'),
    path('requests/<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
]