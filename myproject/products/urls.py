from django.urls import path
from . import views


urlpatterns = [
    path('search/', views.product_search_view, name='product-search'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/view/', views.view_cart, name='view_cart'),
    path('upload-image/', views.upload_product_image, name='product_image_upload'),

]
