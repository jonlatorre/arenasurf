from django.urls import path
from . import views

app_name = 'socios'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_socios, name='dashboard'),
    
    # Socios CRUD
    path('socios/', views.SocioListView.as_view(), name='lista'),
    path('socios/nuevo/', views.SocioCreateView.as_view(), name='crear'),
    path('socios/<int:pk>/', views.SocioDetailView.as_view(), name='detalle'),
    path('socios/<int:pk>/editar/', views.SocioUpdateView.as_view(), name='editar'),
    path('socios/<int:pk>/eliminar/', views.SocioDeleteView.as_view(), name='eliminar'),
    path('socios/<int:pk>/renovar/', views.renovar_socio, name='renovar'),
]
