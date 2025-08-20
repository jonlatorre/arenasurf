from django import forms
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import Socio
from clientes.models import Cliente


class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = [
            'cliente', 'nivel', 'numero_socio', 'fecha_alta', 
            'fecha_vencimiento', 'numero_taquilla', 'numero_guardatablas',
            'precio_anual'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'numero_socio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Se genera automáticamente si se deja vacío'
            }),
            'fecha_alta': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'numero_taquilla': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Opcional'
            }),
            'numero_guardatablas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Opcional'
            }),
            'precio_anual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'cliente': 'Cliente',
            'nivel': 'Nivel de Socio',
            'numero_socio': 'Número de Socio',
            'fecha_alta': 'Fecha de Alta',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'numero_taquilla': 'Número de Taquilla',
            'numero_guardatablas': 'Número de Guardatablas',
            'precio_anual': 'Precio Anual (€)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos opcionales para autogeneración
        self.fields['numero_socio'].required = False
        self.fields['precio_anual'].required = False
        
        # Establecer fecha de alta por defecto
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields['fecha_alta'].initial = today.strftime('%Y-%m-%d')
            # Establecer vencimiento por defecto (1 año después)
            vencimiento = today + timedelta(days=365)
            self.fields['fecha_vencimiento'].initial = vencimiento.strftime('%Y-%m-%d')
        
        # Solo mostrar clientes que no son socios aún (para crear) o el cliente actual (para editar)
        if not self.instance.pk:
            # Para crear nuevo socio, excluir clientes que ya tienen socio
            clientes_disponibles = Cliente.objects.filter(socio__isnull=True, activo=True)
            self.fields['cliente'].queryset = clientes_disponibles
        else:
            # Para editar, permitir el cliente actual y otros disponibles
            clientes_disponibles = Cliente.objects.filter(
                models.Q(socio__isnull=True) | models.Q(pk=self.instance.cliente.pk),
                activo=True
            )
            self.fields['cliente'].queryset = clientes_disponibles
    
    def clean_numero_socio(self):
        numero_socio = self.cleaned_data.get('numero_socio')
        if numero_socio:
            # Verificar que no exista otro socio con el mismo número
            qs = Socio.objects.filter(numero_socio=numero_socio)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un socio con este número.')
        return numero_socio
    
    def clean_numero_taquilla(self):
        numero_taquilla = self.cleaned_data.get('numero_taquilla')
        if numero_taquilla:
            # Verificar que no exista otro socio con la misma taquilla
            qs = Socio.objects.filter(numero_taquilla=numero_taquilla)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Esta taquilla ya está asignada a otro socio.')
        return numero_taquilla
    
    def clean_numero_guardatablas(self):
        numero_guardatablas = self.cleaned_data.get('numero_guardatablas')
        if numero_guardatablas:
            # Verificar que no exista otro socio con el mismo guardatablas
            qs = Socio.objects.filter(numero_guardatablas=numero_guardatablas)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este guardatablas ya está asignado a otro socio.')
        return numero_guardatablas
    
    def clean(self):
        cleaned_data = super().clean()
        nivel = cleaned_data.get('nivel')
        numero_guardatablas = cleaned_data.get('numero_guardatablas')
        precio_anual = cleaned_data.get('precio_anual')
        
        # Establecer precio automáticamente según el nivel si no se proporciona
        if not precio_anual and nivel:
            precios = {
                'BASICO': 300.00,
                'PREMIUM': 500.00,
                'VIP': 800.00,
            }
            cleaned_data['precio_anual'] = precios.get(nivel, 300.00)
        
        # Validaciones según el nivel
        if nivel == 'BASICO':
            # Básico: Solo taquilla opcional, no guardatablas
            if numero_guardatablas:
                self.add_error('numero_guardatablas',
                              'Los socios básicos no tienen acceso a guardatablas.')
        
        elif nivel in ['PREMIUM', 'VIP']:
            # Premium y VIP: Pueden tener ambos servicios
            pass
        
        return cleaned_data
class SocioSearchForm(forms.Form):
    """Formulario para búsqueda y filtrado de socios"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número, nombre, apellidos o email...'
        })
    )
    
    nivel = forms.ChoiceField(
        choices=[('', 'Todos los niveles')] + Socio.NIVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('vigente', 'Vigentes'),
            ('vencido', 'Vencidos'),
            ('inactivo', 'Inactivos'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
