from django import forms
from django.contrib.auth.forms import AuthenticationForm
from backend.models import *
from django.contrib.auth.forms import UserCreationForm


class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ujed.mx'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'contraseña'}))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user    


class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = '__all__'
        exclude = ['estatus', 'fecha_creacion', 'fecha_actualizacion', 'elaborado_por']
        widgets = {
            'nombre_proceso': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fuente': forms.Textarea(attrs={'class': 'form-control'}),
            'formato': forms.FileInput(attrs={'class': 'form-control'}),
            'responsables': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'perfil'):
            direccion = user.perfil.direccion

            # 🔒 Filtrar responsables por dirección
            self.fields['responsables'].queryset = User.objects.filter(
                perfil__direccion=direccion
            )

            # 🧠 Dirección automática (no editable)
            self.fields['direccion'].initial = direccion
            self.fields['direccion'].disabled = True


############################
class ProcesoEditForm(forms.ModelForm):

    class Meta:
        model = Proceso
        fields = '__all__'
        exclude = ['estatus', 'fecha_creacion', 'fecha_actualizacion', 'elaborado_por']
        widgets = {
            'nombre_proceso': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fuente': forms.Textarea(attrs={'class': 'form-control'}),
            'formato': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'responsables': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # 🔒 Bloquear cambio de dirección
        if self.instance and self.instance.pk:
            direccion = self.instance.direccion
            self.fields['direccion'].initial = direccion
            self.fields['direccion'].disabled = True

            # Filtrar responsables por la dirección del proceso
            self.fields['responsables'].queryset = User.objects.filter(
                perfil__direccion=direccion
            )      


class ActividadForm(forms.ModelForm):

    class Meta:
        model = Actividad

        exclude = [
            'proceso',
            'creada_por',
            'revisada_por',
            'fecha_revision',
            'estado',
        ]

        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'herramientas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tiempo_dias_habiles': forms.NumberInput(attrs={'class': 'form-control'}),
            'producto_servicio': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'medio_entrega': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_recurso': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'descrip_recurso': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'responsables': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        proceso = kwargs.pop('proceso', None)

        super().__init__(*args, **kwargs)

        direccion = None

        # Caso 1: proceso enviado desde la vista
        if proceso:
            direccion = proceso.direccion

        # Caso 2: edición de actividad existente
        elif self.instance and self.instance.pk:
            direccion = self.instance.proceso.direccion

        # Caso 3: fallback al perfil del usuario
        elif user and hasattr(user, 'perfil'):
            direccion = user.perfil.direccion

        # Filtrar responsables por dirección
        if direccion:
            self.fields['responsables'].queryset = User.objects.filter(
                perfil__direccion=direccion
            )


class ActividadCheckForm(forms.ModelForm):

    class Meta:
        model = Actividad
        fields = ['estado', 'fecha_revision']

        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_revision': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
        }


class EvidenciaForm(forms.ModelForm):

    class Meta:
        model = Evidencia
        fields = ['archivo', 'descripcion']
        widgets = {
            'archivo': forms.FileInput(attrs={'class':'form-control'}),
            'descripcion': forms.Textarea(attrs={'class':'form-control','rows':2})
        }        


