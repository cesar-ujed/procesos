from rest_framework import serializers
from .models import *

# Serializers define the API representation.
class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'


class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'


class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'                


class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = '__all__'  


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackEvidencia
        fields = '__all__'    