from django import forms
from .models import Bono, UsoBono


class BonoForm(forms.ModelForm):
    class Meta:
        model = Bono
        fields = ['cliente', 'tipo_bono', 'precio', 'fecha_expiracion']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_bono': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_expiracion': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'cliente': 'Cliente',
            'tipo_bono': 'Tipo de Bono',
            'precio': 'Precio (€)',
            'fecha_expiracion': 'Fecha de Expiración',
        }


class UsoBonoForm(forms.ModelForm):
    class Meta:
        model = UsoBono
        fields = ['descripcion', 'fecha_uso']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del uso (opcional)'}),
            'fecha_uso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'descripcion': 'Descripción',
            'fecha_uso': 'Fecha de Uso',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es un formulario nuevo, establecer la fecha actual
        if not self.instance.pk:
            from django.utils import timezone
            today = timezone.now().date()
            self.fields['fecha_uso'].initial = today.strftime('%Y-%m-%d')
