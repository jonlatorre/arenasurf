from django.db import models
from django.urls import reverse
from clientes.models import Cliente


class Bono(models.Model):
    TIPOS_BONOS = [
        (10, '10 Usos'),
        (20, '20 Usos'),
        (30, '30 Usos'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='bonos')
    tipo_bono = models.IntegerField(choices=TIPOS_BONOS, verbose_name='Tipo de Bono')
    usos_totales = models.IntegerField(default=0, verbose_name='Usos Totales')
    usos_restantes = models.IntegerField(verbose_name='Usos Restantes')
    activo = models.BooleanField(default=True)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo en la creación
            self.usos_totales = self.tipo_bono
            self.usos_restantes = self.tipo_bono
        super().save(*args, **kwargs)
    
    def usar_bono(self):
        if self.usos_restantes > 0:
            self.usos_restantes -= 1
            if self.usos_restantes == 0:
                self.activo = False
            self.save()
            return True
        return False
    
    def usos_utilizados(self):
        return self.usos_totales - self.usos_restantes
    
    def porcentaje_uso(self):
        if self.usos_totales > 0:
            return (self.usos_utilizados() / self.usos_totales) * 100
        return 0
    
    def get_absolute_url(self):
        return reverse('bonos:detalle', args=[str(self.pk)])
    
    def __str__(self):
        return f'Bono {self.tipo_bono} usos - {self.cliente.nombre_completo} ({self.usos_restantes} restantes)'
    
    class Meta:
        verbose_name = 'Bono'
        verbose_name_plural = 'Bonos'
        ordering = ['-fecha_compra']


class UsoBono(models.Model):
    bono = models.ForeignKey(Bono, on_delete=models.CASCADE, related_name='usos')
    fecha_uso = models.DateField(verbose_name='Fecha de uso')
    descripcion = models.CharField(max_length=200, blank=True, verbose_name='Descripción del uso')
    
    def save(self, *args, **kwargs):
        # Si no se especifica fecha_uso, usar la fecha actual
        if not self.fecha_uso:
            from django.utils import timezone
            self.fecha_uso = timezone.now().date()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Uso de {self.bono} - {self.fecha_uso.strftime("%d/%m/%Y")}'
    
    class Meta:
        verbose_name = 'Uso de Bono'
        verbose_name_plural = 'Usos de Bonos'
        ordering = ['-fecha_uso']