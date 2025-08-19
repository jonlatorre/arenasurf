from django.urls import path
from . import views

app_name = 'bonos'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Bonos
    path('bonos/', views.BonoListView.as_view(), name='lista'),
    path('bonos/nuevo/', views.BonoCreateView.as_view(), name='crear'),
    path('bonos/<int:pk>/', views.BonoDetailView.as_view(), name='detalle'),
    path('bonos/<int:pk>/editar/', views.BonoUpdateView.as_view(), name='editar'),
    path('bonos/<int:pk>/eliminar/', views.BonoDeleteView.as_view(), name='eliminar'),
    path('bonos/<int:pk>/usar/', views.usar_bono, name='usar'),
    path('bonos/<int:pk>/agregar-uso/', views.agregar_uso_bono, name='agregar_uso'),
]
