from django.urls import path, include
from . import views

urlpatterns = [
    # path('ingest/', views.ingest, name='registrar_ingest'),
    # path('verify_access/', views.verify_access, name='registrar_verify_access'),
    path('', views.overview, name='registrar_overview'),
]
