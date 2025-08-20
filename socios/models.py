from django.db import models
from django.utils import timezone
from clientes.models import Cliente


class Socio(models.Model):
    """Modelo para gestionar socios del surf center"""
    
    NIVEL_CHOICES = [
        ('BASICO', 'Básico'),
        ('PREMIUM', 'Premium'),
        ('VIP', 'VIP'),
    ]
    
    # Relación con cliente
    cliente = models.OneToOneField(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='socio',
        verbose_name='Cliente'
    )
    
    # Información del socio
    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        default='BASICO',
        verbose_name='Nivel de socio'
    )
    
    numero_socio = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Número de socio'
    )
    
    fecha_alta = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de alta'
    )
    
    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de vencimiento'
    )
    
    # Servicios incluidos
    numero_taquilla = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='Número de taquilla'
    )
    
    numero_guardatablas = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='Número de guardatablas'
    )
    
    # Precios según nivel
    precio_anual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio anual'
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['numero_socio']
    
    def __str__(self):
        return f"Socio {self.numero_socio} - {self.cliente.nombre_completo}"
    
    @property
    def esta_vigente(self):
        """Verifica si la membresía está vigente"""
        return self.fecha_vencimiento >= timezone.now().date() and self.activo
    
    @property
    def dias_hasta_vencimiento(self):
        """Calcula días hasta el vencimiento"""
        if not self.esta_vigente:
            return 0
        return (self.fecha_vencimiento - timezone.now().date()).days
    
    @property
    def precio_nivel(self):
        """Retorna información del precio según el nivel"""
        precios = {
            'BASICO': {'anual': 300.00, 'taquilla': True, 'guardatablas': False},
            'PREMIUM': {'anual': 500.00, 'taquilla': True, 'guardatablas': True},
            'VIP': {'anual': 800.00, 'taquilla': True, 'guardatablas': True},
        }
        return precios.get(self.nivel, precios['BASICO'])
    
    def save(self, *args, **kwargs):
        """Override save para asignar número de socio y precio según nivel"""
        # Generar número de socio automáticamente si no existe
        if not self.numero_socio:
            ultimo_numero = Socio.objects.aggregate(
                models.Max('numero_socio')
            )['numero_socio__max']
            if ultimo_numero:
                try:
                    nuevo_numero = str(int(ultimo_numero) + 1).zfill(4)
                except ValueError:
                    nuevo_numero = '0001'
            else:
                nuevo_numero = '0001'
            self.numero_socio = nuevo_numero
        
        # Establecer precio según nivel si no está definido
        if not self.precio_anual:
            self.precio_anual = self.precio_nivel['anual']
        
        super().save(*args, **kwargs)
