from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.db import models
from .forms import UserRegistrationForm, EventoForm
from .models import Evento
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# View para el registro de usuarios
def vista_registro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            grupo_asistentes, creado = Group.objects.get_or_create(name='Asistentes')
            user.groups.add(grupo_asistentes)

            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'evento/registro.html', {'form': form})

# View para el inicio de sesión
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenidx {user.username}!')
            next_url = request.GET.get('next', 'lista_eventos')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'evento/login.html')

# View para el cierre de sesión
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

# Views para la gestión de eventos
class VistaEventos(LoginRequiredMixin, ListView):
    model = Evento
    template_name = 'evento/lista_eventos.html'
    context_object_name = 'eventos'
    paginate_by = 10

    def get_queryset(self):
        usuario = self.request.user

        if usuario.is_superuser or usuario.has_perm('evento.puede_gestionar_eventos'):
            return Evento.objects.all()
        else:
            return Evento.objects.filter(
                models.Q(es_privado=False) |
                models.Q(organizador=usuario) |
                models.Q(asistentes=usuario)
            ).distinct()

# View para el detalle de un evento
class DetalleEvento(LoginRequiredMixin, DetailView):
    model = Evento
    template_name = 'evento/detalle_evento.html'
    context_object_name = 'evento'

    def dispatch(self, request, *args, **kwargs):
        evento = self.get_object()
        if not evento.puede_acceder(request.user):
            messages.error(request, 'No tienes permiso para ver este evento privado.')
            return redirect('acceso_denegado')
        return super().dispatch(request, *args, **kwargs)

# View para crear un nuevo evento
class CrearEvento(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento/evento_form.html'
    success_url = reverse_lazy('lista_eventos')
    permission_required = 'evento.puede_organizar_eventos'

    def form_valid(self, form):
        form.instance.organizador = self.request.user
        messages.success(self.request, '¡Evento creado exitosamente!')
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para crear eventos.')
        return redirect('acceso_denegado')

# View para editar un evento existente
class VistaEditarEvento(LoginRequiredMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'evento/evento_form.html'
    success_url = reverse_lazy('lista_eventos')

    def dispatch(self, request, *args, **kwargs):
        evento = self.get_object()
        usuario = request.user
        
        puede_editar = (
            usuario.is_superuser or
            usuario.has_perm('evento.puede_gestionar_eventos') or
            (usuario.has_perm('evento.puede_organizar_eventos') and evento.organizador == usuario)
        )

        if not puede_editar:
            messages.error(request, 'No tienes permiso para editar este evento.')
            return redirect('access_denegado')

        return super().dispatch(request, *args, **kwargs)

# Mensajes de éxito al actualizar el evento
    def form_valid(self, form):
        messages.success(self.request, '¡Evento actualizado exitosamente!')
        return super().form_valid(form)

# View para eliminar un evento
class VistaEliminarEvento(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Evento
    template_name = 'evento/eliminar_evento.html'
    success_url = reverse_lazy('lista_eventos')
    permission_required = 'evento.puede_gestionar_eventos'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Evento eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, 'Solo los administradores pueden eliminar eventos.')
        return redirect('access_denegado')

# View para acceso denegado
def acceso_denegado(request):
    return render(request, 'evento/acceso_denegado.html', status=403)

# View para el dashboard personalizado
@login_required
def vista_dashboard(request):
    usuario = request.user
    context = {
        'user': usuario,
        'is_admin': usuario.is_superuser or usuario.has_perm('evento.puede_gestionar_eventos'),
        'is_organizer': usuario.has_perm('evento.puede_organizar_eventos'),
        'mis_eventos': Evento.objects.filter(organizador=usuario),
        'eventos_asistentes': Evento.objects.filter(asistentes=usuario),
    }
    return render(request, 'evento/dashboard.html', context)
