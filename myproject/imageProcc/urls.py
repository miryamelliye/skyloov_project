from django.urls import path
from .views import ValidateAndStoreImageView

urlpatterns = [
    path('validate-and-store-image/<int:pk>/', ValidateAndStoreImageView.as_view(), name='validate-and-store-image'),
]