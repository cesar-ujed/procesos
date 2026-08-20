from django.urls import path, include
from rest_framework import routers
from backend import views

router = routers.DefaultRouter()

router.register(r'direccion',       views.DireccionViewSet)
router.register(r'proceso',         views.ProcesoViewSet)
router.register(r'actividad',       views.ActividadViewSet)
router.register(r'evidencia',       views.EvidenciaViewSet)
router.register(r'feedback',        views.FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls))
]  