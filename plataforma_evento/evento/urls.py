from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.vista_dashboard, name='dashboard'),

    # Eventos
    path('', views.VistaEventos.as_view(), name='lista_eventos'),
    path('evento/<int:pk>/', views.DetalleEvento.as_view(), name='detalle_evento'),
    path('evento/crear/', views.CrearEvento.as_view(), name='crear_evento'),
    path('evento/editar/<int:pk>/', views.VistaEditarEvento.as_view(), name='editar_evento'),
    path('evento/eliminar/<int:pk>/', views.VistaEliminarEvento.as_view(), name='eliminar_evento'),

    # Acceso denegado
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),
]

