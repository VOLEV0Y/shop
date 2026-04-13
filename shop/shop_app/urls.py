from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('cart/', cart_view, name='cart'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('increase-cart-item/<int:product_id>/', increase_cart_item, name='increase_cart_item'),
    path('decrease-cart-item/<int:product_id>/', decrease_cart_item, name='decrease_cart_item'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    path('logout/', logout_view, name='logout'),
]
