from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import *
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from backend.models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import IntegrityError
from django.http import FileResponse, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.utils import timezone



# Create your views here.

class IndexView(TemplateView):
    template_name = "home.html"

class LoginView(FormView):
    template_name = 'login.html'  # Ruta al archivo de plantilla
    form_class = BootstrapAuthenticationForm
    success_url = reverse_lazy('procesos')  # Redirigir después de iniciar sesión

    def dispatch(self, request, *args, **kwargs):
        """Cierra la sesión antes de procesar cualquier solicitud a esta vista"""
        logout(request)  # Cierra cualquier sesión activa
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Inicia sesión al validar el formulario"""
        user = form.get_user()  # Obtiene el usuario autenticado
        login(self.request, user)  # Inicia la sesión del usuario
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        """Maneja el caso en que el formulario no es válido (credenciales incorrectas)"""
        messages.error(self.request, "Usuario o contraseña incorrectos.")  # Envía un mensaje de error
        return super().form_invalid(form)  # Vuelve a mostrar el formulario con errores

    def get_success_url(self):
        """Redirigir después del login, con soporte para ?next="" en la URL"""
        return self.request.GET.get('next', self.success_url)
    

# Cerrar sesión
class LogoutView(View):
    def get(self, request):
        # Cierra la sesión del usuario
        logout(request)
        # Redirige a la página de inicio u otra página después de cerrar la sesión
        return redirect(reverse('login'))
    

class UserRegisterView(FormView):
    template_name = 'signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            form.save()
            messages.success(self.request, 'Usuario creado correctamente.')
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, 'El usuario ya existe')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Las contraseñas no coinciden')
        return super().form_invalid(form)
        


# @login_required
class ProcesoCreateView(CreateView):
    model = Proceso
    form_class = ProcesoForm
    template_name = 'crear_proceso.html'
    success_url = reverse_lazy('procesos')  # Redirigir después de la creación

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.direccion = self.request.user.perfil.direccion
        form.instance.elaborado_por = self.request.user
        return super().form_valid(form)



class ProcesosListView(ListView):
    model = Proceso
    template_name = 'procesos.html'
    context_object_name = 'procesos'

    def get_queryset(self):
        user = self.request.user
        query = self.request.GET.get('q', '').strip()

        # queryset base
        if user.is_superuser:
            qs = Proceso.objects.all()
        else:
            qs = Proceso.objects.filter(
                direccion_id=user.perfil.direccion_id
            )

        # búsqueda general
        if query:
            qs = qs.filter(
                Q(nombre_proceso__icontains=query) |
                Q(responsables__username__icontains=query) |
                Q(direccion__nombre__icontains=query)
            ).distinct()

            # búsqueda por estatus textual
            q_lower = query.lower()
            if q_lower in ['aprobado', 'pendiente']:
                qs = qs.filter(
                    aprobado=(q_lower == 'aprobado')
                )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProcesoDetailView(DetailView):
    model = Proceso
    template_name = 'proceso_detail.html'
    context_object_name = 'proceso'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proceso = self.get_object()

        total_actividades = proceso.actividades.count()

        aprobadas = proceso.actividades.filter(
            estado='aprobada'
        ).count()

        porcentaje = 0

        if total_actividades > 0:
            porcentaje = int((aprobadas / total_actividades) * 100)

        context['total_actividades'] = total_actividades
        context['actividades_aprobadas'] = aprobadas
        context['porcentaje'] = porcentaje

        # lista de actividades
        context['actividades'] = proceso.actividades.all()

        return context


class EliminarProcesoView(PermissionRequiredMixin, DeleteView):
    model = Proceso
    template_name = 'confirmar_eliminacion.html'
    success_url = reverse_lazy('procesos')
    permission_required = 'backend.delete_proceso'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        proceso = self.get_object()

        # Si está completado y NO es superadmin → bloqueado
        if proceso.estatus == 'completado' and not request.user.is_superuser:
            raise PermissionDenied(
                "No puedes eliminar un proceso completado."
            )

        return super().dispatch(request, *args, **kwargs)


class ProcesoEditView(PermissionRequiredMixin, UpdateView):
    model = Proceso
    template_name = 'proceso_edit.html'
    form_class = ProcesoEditForm
    success_url = reverse_lazy('procesos')
    permission_required = 'backend.change_proceso'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        proceso = self.get_object()

        # Bloqueo si está completado
        if proceso.estatus == 'completado' and not request.user.is_superuser:
            raise PermissionDenied(
                "No puedes editar un proceso completado."
            )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Blindaje extra: no permitir cambio de dirección
        form.instance.direccion = self.get_object().direccion
        return super().form_valid(form)  


class ActividadCreateView(CreateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'crear_actividad.html'

    # 🔹 Centralizamos la obtención del proceso (DRY)
    def get_proceso(self):
        return get_object_or_404(Proceso, pk=self.kwargs['pk'])

    # 🔹 Contexto adicional para el template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proceso'] = self.get_proceso()
        return context

    # 🔥 Inyección de dependencias al form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['proceso'] = self.get_proceso()
        return kwargs

    # 🔹 Asignaciones antes de guardar
    def form_valid(self, form):
        form.instance.proceso = self.get_proceso()
        form.instance.creada_por = self.request.user

        messages.success(self.request, "Actividad creada correctamente.")

        return super().form_valid(form)

    # 🔹 Debug opcional
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    # 🔹 Redirección
    def get_success_url(self):
        return reverse('proceso_detail', kwargs={'pk': self.object.proceso.pk})



class ActividadUpdate(PermissionRequiredMixin, UpdateView):
    model = Actividad
    template_name = 'editar_actividad.html'
    form_class = ActividadForm
    permission_required = 'backend.change_actividad'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
            actividad = self.get_object()

            # Corrección: evaluamos el campo 'estado'
            if actividad.estado == 'aprobada' and not request.user.is_superuser:
                raise PermissionDenied(
                    "No puedes editar una actividad aprobada."
                )

            return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proceso'] = self.object.proceso
        return context

    def get_success_url(self):
        return reverse(
            'proceso_detail',
            kwargs={'pk': self.object.proceso_id}
        )


class EliminarActividadView(DeleteView):
    model = Actividad
    template_name = 'confirmar_eliminacion.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        messages.success(
            request,
            f"La actividad {self.object.numero} fue eliminada"
        )

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('proceso_detail', kwargs={'pk': self.object.proceso.pk})
    

class ActividadDetailView(LoginRequiredMixin, DetailView):
    model = Actividad
    template_name = 'actividad_detail.html'
    context_object_name = 'actividad'

    def get_queryset(self):
        # Traemos la actividad junto con sus evidencias, los usuarios que las subieron
        # y los feedbacks asociados en una sola consulta optimizada.
        return super().get_queryset().prefetch_related(
            'evidencias__subida_por', 
            'evidencias__feedbacks__creado_por'
        )       


def cambiar_estado_evidencia(request, pk):

    evidencia = get_object_or_404(Evidencia, pk=pk)

    # 🔒 BLOQUEO REAL
    if evidencia.actividad.estado == "aprobada":
        return redirect("actividad_detail", pk=evidencia.actividad.pk)

    if request.method == "POST":

        nuevo_estado = request.POST.get("estado")

        if nuevo_estado in ["pendiente", "aprobada", "correccion"]:
            evidencia.estado = nuevo_estado
            evidencia.save()

    return redirect("actividad_detail", pk=evidencia.actividad.pk)
    

class SubirEvidenciaView(CreateView):

    model = Evidencia
    form_class = EvidenciaForm
    template_name = 'subir_archivos.html'

    def form_valid(self, form):
        actividad = Actividad.objects.get(pk=self.kwargs['pk'])

        form.instance.actividad = actividad
        form.instance.subida_por = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'actividad_detail',
            kwargs={'pk': self.object.actividad.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        actividad = Actividad.objects.get(pk=self.kwargs['pk'])

        context['actividad'] = actividad
        context['proceso'] = actividad.proceso

        return context
    

class CambiarEstatusProcesoView(PermissionRequiredMixin, View):
    permission_required = 'backend.change_proceso'
    raise_exception = True  # devuelve 403 en vez de redirigir silencioso

    def post(self, request, pk):
        proceso = get_object_or_404(Proceso, pk=pk)
        nuevo_estatus = request.POST.get('estatus')

        TRANSICIONES_VALIDAS = {
            'pendiente': ['en_ejecucion'],
            'en_ejecucion': ['completado'],
            'completado': [],
        }

        # 1️⃣ validar que el estatus exista
        if nuevo_estatus not in dict(Proceso.ESTADO):
            return redirect('proceso_detail', pk=pk)

        # 2️⃣ validar transición
        if nuevo_estatus in TRANSICIONES_VALIDAS.get(proceso.estatus, []):
            proceso.estatus = nuevo_estatus
            proceso.save()

        return redirect('proceso_detail', pk=pk)
    

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        procesos = Proceso.objects.all()
        actividades = Actividad.objects.all()

        context['total_procesos'] = procesos.count()
        context['total_actividades'] = actividades.count()

        # Actividades aprobadas
        context['actividades_aprobadas'] = actividades.filter(
            estado='aprobada'
        ).count()

        # Actividades pendientes
        context['actividades_pendientes'] = actividades.filter(
            estado='pendiente'
        ).count()

        # Actividades en revisión
        context['actividades_en_revision'] = actividades.filter(
            estado='en_revision'
        ).count()

        return context
    

@login_required
def cambiar_estado_evidencia(request, pk):
    evidencia = get_object_or_404(Evidencia, pk=pk)
    
    # VALIDACIÓN DE GRUPO MANUAL
    es_admin_dir = request.user.groups.filter(name='admin_direccion').exists() or request.user.is_superuser
    
    if not es_admin_dir:
        messages.error(request, "Acceso denegado: Solo Dirección puede evaluar evidencias.")
        return redirect('actividad_detail', pk=evidencia.actividad.pk)

    # Validamos el estado de la Actividad
    if evidencia.actividad.estado == 'aprobada':
        messages.error(request, "No puedes modificar evidencias de una actividad cerrada/aprobada.")
        return redirect('actividad_detail', pk=evidencia.actividad.pk)

    if request.method == "POST":
        nuevo_estado = request.POST.get('estado')
        evidencia.estado = nuevo_estado
        evidencia.save()
        messages.success(request, f"Evidencia actualizada a {evidencia.get_estado_display()}.")
        
    return redirect('actividad_detail', pk=evidencia.actividad.pk)



def crear_feedback(request, pk):

    evidencia = get_object_or_404(Evidencia, pk=pk)

    if request.method == "POST":

        comentario = request.POST.get("comentario")

        FeedbackEvidencia.objects.create(
            evidencia=evidencia,
            comentario=comentario,
            creado_por=request.user
        )

    return redirect("actividad_detail", pk=evidencia.actividad.pk)


@login_required
def cambiar_estatus_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    
    # Validación de grupo (asegúrate de que coincida con lo que usas)
    es_admin_dir = request.user.groups.filter(name='admin_direccion').exists() or request.user.is_superuser
    
    if not es_admin_dir:
        messages.error(request, "Acceso denegado: Solo la Dirección puede cerrar actividades.")
        return redirect('actividad_detail', pk=pk)

    # 1. Cambiamos 'completado' por 'aprobada'
    if actividad.estado == 'aprobada':
        messages.warning(request, "La actividad ya está cerrada.")
        return redirect('actividad_detail', pk=pk)

    if request.method == "POST":
        nuevo_estatus = request.POST.get('estado')
        
        # 2. AQUÍ ESTABA EL DETALLE: Evaluamos si llega 'aprobada'
        if nuevo_estatus == 'aprobada':
            actividad.estado = 'aprobada'
            actividad.fecha_revision = timezone.now()
            actividad.revisada_por = request.user
            actividad.save()
            messages.success(request, "Actividad aprobada y bloqueada exitosamente.")
        else:
            actividad.estado = 'pendiente'
            actividad.save()
            messages.info(request, "Estatus actualizado a pendiente.")
            
    return redirect('actividad_detail', pk=pk)



class EvidenciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Evidencia
    fields = ['archivo'] 
    template_name = 'corregir_evidencia.html'

    def form_valid(self, form):
        # 1. Regresamos el estatus a pendiente
        form.instance.estado = 'pendiente'
        form.instance.subida_por = self.request.user
        
        # 2. CREAMOS EL COMENTARIO AUTOMÁTICO DE TRAZABILIDAD
        Feedback.objects.create(
            evidencia=form.instance,
            creado_por=self.request.user,
            comentario="🔄 [SISTEMA]: El usuario ha subido una nueva versión del archivo para su revisión."
        )
        
        # 3. Mandamos el mensaje verde temporal
        messages.success(self.request, "✅ Archivo corregido. Se ha notificado a Dirección para su revisión.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('actividad_detail', kwargs={'pk': self.object.actividad.pk})