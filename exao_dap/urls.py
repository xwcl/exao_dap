"""exao_dap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

from rest_framework.authtoken import views as authtoken_views
from rest_framework import routers

from . import views
from . import signals  # ensure registration at startup
from .registrar import views as registrar_views

router = routers.SimpleRouter()
router.register(r'registrar/datasets', registrar_views.DatasetViewSet)
router.register(r'registrar/data', registrar_views.DatumViewSet)

admin.site.site_header = 'DAP administration'

urlpatterns = [
    path('', include(router.urls)),
    path('obtain-auth-token/', authtoken_views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('registrar/', include('exao_dap.registrar.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('', include('social_django.urls', namespace='social')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('users/me/', views.redirect_to_profile, name='redirect_to_profile'),
    path('users/<str:username>/', views.user_profile, name='user_profile'),
    path('', views.home, name='home'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),]
