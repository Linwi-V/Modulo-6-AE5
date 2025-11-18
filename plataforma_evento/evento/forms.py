from django import forms
from django.contrib.auth.models import User
from .models import Evento

# Formulario para registrar usuarios
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd.get('password2')


# Formulario para crear o editar eventos
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'titulo',
            'descripcion',
            'tipo_evento',
            'fecha',
            'ubicacion',
            'es_privado',
            'asistentes',
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'asistentes': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'tipo_evento': 'Tipo de Evento',
            'fecha': 'Fecha del Evento',
            'ubicacion': 'Ubicación',
            'es_privado': 'Evento Privado',
            'asistentes': 'Asistentes',
        }
