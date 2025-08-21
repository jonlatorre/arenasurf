from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Bono, UsoBono
from clientes.models import Cliente
from .forms import BonoForm, UsoBonoForm
from arenasurf.mixins import StaffRequiredMixin, staff_required


# Vistas de Bonos
class BonoListView(StaffRequiredMixin, ListView):
    model = Bono
    template_name = 'bonos/bono_list.html'
    context_object_name = 'bonos'
    paginate_by = 20
    
    def get_queryset(self):
        return Bono.objects.select_related('cliente').order_by('-fecha_compra')


class BonoDetailView(StaffRequiredMixin, DetailView):
    model = Bono
    template_name = 'bonos/bono_detail.html'
    context_object_name = 'bono'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usos'] = self.object.usos.all()
        context['uso_form'] = UsoBonoForm()
        return context


class BonoCreateView(StaffRequiredMixin, CreateView):
    model = Bono
    form_class = BonoForm
    template_name = 'bonos/bono_form.html'
    success_url = reverse_lazy('bonos:lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bono creado exitosamente.')
        return super().form_valid(form)


class BonoUpdateView(StaffRequiredMixin, UpdateView):
    model = Bono
    form_class = BonoForm
    template_name = 'bonos/bono_form.html'
    success_url = reverse_lazy('bonos:lista')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bono actualizado exitosamente.')
        return super().form_valid(form)


class BonoDeleteView(StaffRequiredMixin, DeleteView):
    model = Bono
    template_name = 'bonos/bono_confirm_delete.html'
    success_url = reverse_lazy('bonos:lista')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Bono eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Función para usar un bono (uso rápido sin formulario)
@staff_required
def usar_bono(request, pk):
    bono = get_object_or_404(Bono, pk=pk)
    
    if request.method == 'POST':
        if bono.usar_bono():
            # Crear registro de uso rápido con fecha actual
            from django.utils import timezone
            UsoBono.objects.create(
                bono=bono,
                fecha_uso=timezone.now().date(),
                descripcion="Uso rápido"
            )
            messages.success(request, f'Bono usado exitosamente. Quedan {bono.usos_restantes} usos.')
        else:
            messages.error(request, 'No se puede usar este bono. No tiene usos restantes.')
    
    return redirect('bonos:detalle', pk=bono.pk)


# Vista para agregar uso de bono con formulario completo
@staff_required
def agregar_uso_bono(request, pk):
    bono = get_object_or_404(Bono, pk=pk)
    
    if not bono.activo or bono.usos_restantes <= 0:
        messages.error(request, 'No se puede usar este bono. No tiene usos restantes.')
        return redirect('bonos:detalle', pk=bono.pk)
    
    if request.method == 'POST':
        form = UsoBonoForm(request.POST)
        if form.is_valid():
            if bono.usar_bono():
                uso = form.save(commit=False)
                uso.bono = bono
                uso.save()
                messages.success(request, f'Uso registrado exitosamente. Quedan {bono.usos_restantes} usos.')
                return redirect('bonos:detalle', pk=bono.pk)
            else:
                messages.error(request, 'Error al usar el bono.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UsoBonoForm()
    
    return render(request, 'bonos/agregar_uso.html', {
        'form': form,
        'bono': bono,
    })


# Vista del dashboard
@staff_required
def dashboard(request):
    bonos_activos = Bono.objects.filter(activo=True).count()
    bonos_agotados = Bono.objects.filter(activo=False).count()
    clientes_activos = Cliente.objects.filter(activo=True).count()
    usos_recientes = UsoBono.objects.select_related('bono__cliente').order_by('-fecha_uso')[:10]
    
    context = {
        'bonos_activos': bonos_activos,
        'bonos_agotados': bonos_agotados,
        'clientes_activos': clientes_activos,
        'usos_recientes': usos_recientes,
    }
    
    return render(request, 'bonos/dashboard.html', context)
