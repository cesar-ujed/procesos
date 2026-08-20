from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Direccion(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuario')
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, verbose_name='direccion')

    class Meta:
        verbose_name='perfil'
        verbose_name_plural='perfiles'
        ordering=['-id']

    def __str__(self):
        return self.user.username


class Proceso(models.Model):
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('en_ejecucion', 'En ejecucion'),
        ('completado', 'Completado'),
    ]

    elaborado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='procesos_elaborados'
    )
    nombre_proceso      = models.TextField()
    direccion           = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    descripcion         = models.TextField()
    fuente              = models.TextField()
    formato             = models.FileField(upload_to="formatos/", blank=True, null=True)
    responsables = models.ManyToManyField(
        User,
        related_name='procesos_responsables'
    )    
    estatus             = models.CharField(max_length=90, choices=ESTADO, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['nombre_proceso']
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'    

    def __str__(self):
        return self.nombre_proceso


class Actividad(models.Model):

    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
    ]

    proceso = models.ForeignKey(
        Proceso,
        on_delete=models.CASCADE,
        related_name='actividades'
    )

    responsables = models.ManyToManyField(
        User,
        related_name='actividades_responsables'
    )

    numero = models.PositiveIntegerField()
    descripcion = models.TextField()
    herramientas = models.TextField()
    tiempo_dias_habiles = models.PositiveIntegerField()

    producto_servicio = models.TextField()
    destinatario = models.CharField(max_length=255)
    medio_entrega = models.TextField()

    tipo_recurso = models.TextField()
    descrip_recurso = models.TextField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='pendiente'
    )

    creada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actividades_creadas'
    )

    revisada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_revisadas'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['numero']
        unique_together = ('proceso', 'numero')

    def __str__(self):
        return f"{self.proceso.nombre_proceso} - Actividad {self.numero}"
    

class Evidencia(models.Model):

    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('correccion', 'Requiere corrección'),
    ]

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )

    archivo = models.FileField(upload_to='evidencias/')
    descripcion = models.TextField(blank=True, null=True)

    subida_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evidencias_subidas'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='pendiente'
    )

    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia {self.id} - Actividad {self.actividad.numero}"
    

class FeedbackEvidencia(models.Model):

    evidencia = models.ForeignKey(
        Evidencia,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )

    comentario = models.TextField()

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback evidencia {self.evidencia.id}"    
    