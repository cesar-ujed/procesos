from django import urls, views
from .views import *
from django.urls import path
from frontend import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('',                                    LoginView.as_view(),                    name="login"),
    path('logout/',                             LogoutView.as_view(),                   name='logout'),
    path('registrarme/',                        UserRegisterView.as_view() ,            name='registro'),
    path('home/',                               IndexView.as_view(),                    name='home'),
    path('nuevo_proceso/',                      ProcesoCreateView.as_view(),            name='createProcess'),
    path('procesos/',                           ProcesosListView.as_view(),             name='procesos'),
    path('proceso/<int:pk>/',                   ProcesoDetailView.as_view(),            name='proceso_detail'),
    path('eliminar_proceso/<int:pk>/',          views.EliminarProcesoView.as_view(),    name='eliminar_proceso'),
    path('editar/<int:pk>',                     ProcesoEditView.as_view(),              name='editar_proceso'),
    path('proceso/<int:pk>/actividad/nueva/',   ActividadCreateView.as_view(),          name='actividad_crear'),
    path('editar_actividad/<int:pk>/',          ActividadUpdate.as_view(),              name='editaractividad'),
    path('eliminar_actividad/<int:pk>/',        views.EliminarActividadView.as_view(),  name='eliminar_actividad'),
    path('actividad/<int:pk>/',                 ActividadDetailView.as_view(),          name='actividad_detail'),
    # path('obtener_evidencia/<int:pdf_id>/',     views.obtener_pdf,                      name='obtener_pdf'),
    path('evidencia/<int:pk>/estado/', views.cambiar_estado_evidencia, name='cambiar_estado_evidencia'),
    path('actividad/<int:pk>/subir-evidencia/', SubirEvidenciaView.as_view(),           name='subir_evidencia'),
    path('proceso/<int:pk>/cambiar-estatus/',   CambiarEstatusProcesoView.as_view(),    name='proceso_cambiar_estatus'),
    path('dashboard/',                          DashboardView.as_view(),                name='dashboard'),
    path("evidencia/<int:pk>/feedback/",        crear_feedback,                         name="crear_feedback"),
    path('actividad/<int:pk>/cambiar-estatus/', views.cambiar_estatus_actividad, name='cambiar_estatus_actividad'),
    path('evidencia/<int:pk>/corregir/', views.EvidenciaUpdateView.as_view(), name='corregir_evidencia'),

    # reset password
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset_done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
