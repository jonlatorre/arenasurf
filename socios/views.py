from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Socio
from .forms import SocioForm


class SocioListView(ListView):
    model = Socio
    template_name = 'socios/socio_list.html'
    context_object_name = 'socios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Socio.objects.select_related('cliente').order_by('numero_socio')
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_socio__icontains=search) |
                Q(cliente__nombre__icontains=search) |
                Q(cliente__apellidos__icontains=search) |
                Q(cliente__email__icontains=search)
            )
        
        # Filtro por nivel
        nivel = self.request.GET.get('nivel')
        if nivel:
            queryset = queryset.filter(nivel=nivel)
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado == 'vigente':
            today = timezone.now().date()
            queryset = queryset.filter(fecha_vencimiento__gte=today, activo=True)
        elif estado == 'vencido':
            today = timezone.now().date()
            queryset = queryset.filter(fecha_vencimiento__lt=today)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['nivel'] = self.request.GET.get('nivel', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['nivel_choices'] = Socio.NIVEL_CHOICES
        return context


class SocioDetailView(DetailView):
    model = Socio
    template_name = 'socios/socio_detail.html'
    context_object_name = 'socio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información adicional si es necesario
        return context


class SocioCreateView(CreateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    success_url = reverse_lazy('socios:lista')
    
    def form_valid(self, form):
        # El número de socio y precio se generan automáticamente en el método save del modelo
        messages.success(self.request, 'Socio creado exitosamente.')
        return super().form_valid(form)


class SocioUpdateView(UpdateView):
    model = Socio
    form_class = SocioForm
    template_name = 'socios/socio_form.html'
    success_url = reverse_lazy('socios:lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Socio actualizado exitosamente.')
        return super().form_valid(form)


class SocioDeleteView(DeleteView):
    model = Socio
    template_name = 'socios/socio_confirm_delete.html'
    success_url = reverse_lazy('socios:lista')
    
    def delete(self, request, *args, **kwargs):
        # Marcar como inactivo en lugar de eliminar
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        messages.success(self.request, 'Socio desactivado exitosamente.')
        return redirect(self.success_url)


def dashboard_socios(request):
    """Vista del dashboard de socios"""
    today = timezone.now().date()
    
    # Estadísticas
    total_socios = Socio.objects.filter(activo=True).count()
    socios_vigentes = Socio.objects.filter(
        activo=True,
        fecha_vencimiento__gte=today
    ).count()
    socios_vencidos = Socio.objects.filter(
        fecha_vencimiento__lt=today,
        activo=True
    ).count()
    
    # Próximos vencimientos (30 días)
    fecha_limite = today + timedelta(days=30)
    proximos_vencimientos = Socio.objects.filter(
        activo=True,
        fecha_vencimiento__gte=today,
        fecha_vencimiento__lte=fecha_limite
    ).select_related('cliente').order_by('fecha_vencimiento')[:10]
    
    # Socios por nivel
    socios_basico = Socio.objects.filter(activo=True, nivel='BASICO').count()
    socios_premium = Socio.objects.filter(activo=True, nivel='PREMIUM').count()
    socios_vip = Socio.objects.filter(activo=True, nivel='VIP').count()
    
    context = {
        'total_socios': total_socios,
        'socios_vigentes': socios_vigentes,
        'socios_vencidos': socios_vencidos,
        'proximos_vencimientos': proximos_vencimientos,
        'socios_basico': socios_basico,
        'socios_premium': socios_premium,
        'socios_vip': socios_vip,
    }
    
    return render(request, 'socios/dashboard.html', context)


def renovar_socio(request, pk):
    """Vista para renovar la membresía de un socio"""
    socio = get_object_or_404(Socio, pk=pk)
    
    if request.method == 'POST':
        # Renovar por un año más
        socio.fecha_vencimiento = socio.fecha_vencimiento + timedelta(days=365)
        socio.activo = True
        socio.save()
        
        messages.success(
            request, 
            f'Membresía renovada hasta {socio.fecha_vencimiento.strftime("%d/%m/%Y")}'
        )
        return redirect('socios:detalle', pk=socio.pk)
    
    return render(request, 'socios/renovar_socio.html', {'socio': socio})
