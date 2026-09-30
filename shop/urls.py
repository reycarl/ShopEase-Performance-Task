from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("manage/products/", views.product_manage, name="product_manage"),
    path("manage/products/add/", views.product_create, name="product_create"),
    path("manage/products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("manage/products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/summary/", views.checkout_summary, name="checkout_summary"),
    path("orders/<int:pk>/confirmation/", views.order_confirmation, name="order_confirmation"),
]
