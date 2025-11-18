from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    TIPO_EVENTO_OPCIONES = [
        ('conferencia', 'Conferencia'),
        ('concierto', 'Concierto'),
        ('seminario', 'Seminario'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    tipo_evento = models.CharField(
        max_length=20, 
        choices=TIPO_EVENTO_OPCIONES,
        verbose_name='Tipo de Evento'
    )
    fecha = models.DateTimeField(verbose_name='Fecha del Evento')
    ubicacion = models.CharField(max_length=300, verbose_name='Ubicación')
    es_privado = models.BooleanField(
        default=False, 
        verbose_name='Evento Privado'
    )
    organizador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='eventos_organizados',
        verbose_name='Organizador'
    )
    asistentes = models.ManyToManyField(
        User, 
        related_name='eventos_asistidos', 
        blank=True,
        verbose_name='Asistentes'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha']
        permissions = [
            ('puede_gestionar_eventos', 'Puede gestionar todos los eventos'),
            ('puede_organizar_eventos', 'Puede organizar eventos'),
        ]

    def __str__(self):
        return self.titulo

    def puede_acceder(self, usuario):
#Verifica si un usuario puede acceder al evento
        if not self.es_privado:
            return True
        return usuario == self.organizador or usuario in self.asistentes.all() or usuario.is_superuser
