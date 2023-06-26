from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt import views as jwt_views

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
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('reg/', include('userRegistration.urls')),
    path('img/', include('imageProcc.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)