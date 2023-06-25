from django.urls import path
from . import views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
    ),
    public=True,
)


urlpatterns = [
    # path('api/products/search/', ProductSearchView.as_view(), name='product_search'),
    path('search/', views.product_search_view, name='product-search'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/view/', views.view_cart, name='view_cart'),
    path('upload-image/', views.upload_product_image, name='product_image_upload'),
    path('store-image/<int:pk>/', views.validate_and_store_image, name='product_image_store'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

]
