from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Cliente
from bonos.models import Bono, UsoBono
from socios.models import Socio


class ClienteRegistrationForm(UserCreationForm):
    """Formulario para registro de cliente con usuario"""
    email = forms.EmailField(required=True, label="Email")
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    apellidos = forms.CharField(max_length=100, required=True, label="Apellidos")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono")
    fecha_nacimiento = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de nacimiento"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Crear el cliente asociado
            Cliente.objects.create(
                usuario=user,
                nombre=self.cleaned_data["nombre"],
                apellidos=self.cleaned_data["apellidos"],
                email=self.cleaned_data["email"],
                telefono=self.cleaned_data["telefono"],
                fecha_nacimiento=self.cleaned_data["fecha_nacimiento"]
            )
        return user


class ClienteRegistrationView(CreateView):
    """Vista para registro de nuevos clientes"""
    form_class = ClienteRegistrationForm
    template_name = 'clientes/registro.html'
    success_url = reverse_lazy('clientes:panel')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Autenticar automáticamente al usuario después del registro
        user = form.save()
        login(self.request, user)
        messages.success(self.request, '¡Registro exitoso! Bienvenido a Arena Surf.')
        return response


class ClientePanelView(LoginRequiredMixin, TemplateView):
    """Panel principal del cliente"""
    template_name = 'clientes/panel.html'
    login_url = '/account/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug: verificar usuario actual
        print(f"DEBUG: Usuario actual: {self.request.user.username}")
        print(f"DEBUG: Usuario autenticado: {self.request.user.is_authenticated}")
        
        # Intentar obtener el cliente asociado al usuario
        cliente = None
        if hasattr(self.request.user, 'cliente'):
            cliente = self.request.user.cliente
            print(f"DEBUG: Cliente encontrado: {cliente.nombre_completo}")
        else:
            print(f"DEBUG: Usuario {self.request.user.username} no tiene cliente asociado")
            messages.error(self.request, 'No tienes un perfil de cliente. Por favor, contacta con el administrador para vincular tu cuenta.')
            context['error'] = 'no_cliente'
            return context
        
        # Información del cliente
        context['cliente'] = cliente
        
        # Información de socio si existe
        socio = None
        es_socio = False
        if hasattr(cliente, 'socio'):
            socio = cliente.socio
            es_socio = True
            print(f"DEBUG: Cliente es socio: {socio.numero_socio}")
        else:
            print(f"DEBUG: Cliente no es socio")
            
        context['socio'] = socio
        context['es_socio'] = es_socio
        
        # Bonos del cliente
        from bonos.models import Bono, UsoBono
        
        bonos_activos = Bono.objects.filter(cliente=cliente, activo=True)
        bonos_agotados = Bono.objects.filter(cliente=cliente, activo=False)
        
        print(f"DEBUG: Bonos activos: {bonos_activos.count()}")
        print(f"DEBUG: Bonos agotados: {bonos_agotados.count()}")
        
        context['bonos_activos'] = bonos_activos
        context['bonos_agotados'] = bonos_agotados
        context['total_bonos'] = bonos_activos.count() + bonos_agotados.count()
        
        # Últimos usos de bonos
        ultimos_usos = UsoBono.objects.filter(
            bono__cliente=cliente
        ).order_by('-fecha_uso')[:10]
        context['ultimos_usos'] = ultimos_usos
        
        print(f"DEBUG: Últimos usos: {ultimos_usos.count()}")
        
        return context


@login_required
def cliente_perfil_ajax(request):
    """Vista AJAX para obtener datos del perfil del cliente"""
    try:
        cliente = request.user.cliente
        data = {
            'nombre_completo': cliente.nombre_completo,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'fecha_registro': cliente.created_at.strftime('%d/%m/%Y'),
            'bonos_activos': Bono.objects.filter(cliente=cliente, activo=True).count(),
            'bonos_agotados': Bono.objects.filter(cliente=cliente, activo=False).count(),
        }
        
        # Información de socio si existe
        try:
            socio = cliente.socio
            data['socio'] = {
                'numero': socio.numero_socio,
                'nivel': socio.get_nivel_display(),
                'vigente': socio.esta_vigente,
                'vencimiento': socio.fecha_vencimiento.strftime('%d/%m/%Y'),
                'dias_restantes': socio.dias_hasta_vencimiento,
                'taquilla': socio.numero_taquilla,
                'guardatablas': socio.numero_guardatablas,
            }
        except Socio.DoesNotExist:
            data['socio'] = None
            
        return JsonResponse(data)
        
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)


@login_required
def cliente_bonos_ajax(request):
    """Vista AJAX para obtener bonos del cliente"""
    try:
        cliente = request.user.cliente
        bonos = Bono.objects.filter(cliente=cliente).order_by('-fecha_compra')
        
        bonos_data = []
        for bono in bonos:
            usos = UsoBono.objects.filter(bono=bono).order_by('-fecha_uso')
            bonos_data.append({
                'id': bono.id,
                'tipo': f'{bono.tipo_bono} usos',
                'usos_totales': bono.usos_totales,
                'usos_utilizados': bono.usos_utilizados(),
                'usos_restantes': bono.usos_restantes,
                'activo': bono.activo,
                'fecha_compra': bono.fecha_compra.strftime('%d/%m/%Y'),
                'precio': str(bono.precio) if bono.precio else '-',
                'usos': [
                    {
                        'fecha': uso.fecha_uso.strftime('%d/%m/%Y'),
                        'descripcion': uso.descripcion or ''
                    } for uso in usos[:5]  # Últimos 5 usos
                ]
            })
            
        return JsonResponse({'bonos': bonos_data})
        
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
