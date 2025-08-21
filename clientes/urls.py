from django.urls import path
from . import views
from . import panel_views

app_name = 'clientes'

urlpatterns = [
    # URLs para administración (staff)
    path('', views.ClienteListView.as_view(), name='lista'),
    path('nuevo/', views.ClienteCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='eliminar'),
    
    # URLs para panel de cliente
    path('registro/', panel_views.ClienteRegistrationView.as_view(), name='registro'),
    path('panel/', panel_views.ClientePanelView.as_view(), name='panel'),
    path('api/perfil/', panel_views.cliente_perfil_ajax, name='perfil_ajax'),
    path('api/bonos/', panel_views.cliente_bonos_ajax, name='bonos_ajax'),
]
