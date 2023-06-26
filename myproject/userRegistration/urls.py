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

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

]
