from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_evento', 'fecha', 'organizador', 'es_privado', 'fecha_creacion']
    list_filter = ['tipo_evento', 'es_privado', 'fecha']
    search_fields = ['titulo', 'descripcion', 'ubicacion']
    date_hierarchy = 'fecha'
    filter_horizontal = ['asistentes']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo_evento')
        }),
        ('Detalles del Evento', {
            'fields': ('fecha', 'ubicacion', 'es_privado')
        }),
        ('Gestión de Usuarios', {
            'fields': ('organizador', 'asistentes')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Asigna el organizador automáticamente si es un nuevo evento
        if not change:
            obj.organizador = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superusuarios o con permiso de gestionar todos los eventos ven todo
        if request.user.is_superuser or request.user.has_perm('evento.puede_gestionar_eventos'):
            return qs
        # Organizadores solo ven sus eventos
        elif request.user.has_perm('evento.puede_organizar_eventos'):
            return qs.filter(organizador=request.user)
        # Otros usuarios no ven eventos
        return qs.none()

    def has_change_permission(self, request, obj=None):
        # Superusuarios o quienes gestionan eventos pueden cambiar cualquiera
        if request.user.is_superuser or request.user.has_perm('evento.puede_gestionar_eventos'):
            return True
        # Organizadores solo pueden cambiar sus eventos
        if obj and request.user.has_perm('evento.puede_organizar_eventos') and obj.organizador == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios o quienes gestionan eventos pueden borrar
        if request.user.is_superuser or request.user.has_perm('evento.puede_gestionar_eventos'):
            return True
        return False

