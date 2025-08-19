from django.db import models
from django.urls import reverse


class Cliente(models.Model):
    """Modelo para representar un cliente del surf center"""
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    email = models.EmailField(unique=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellidos', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    def get_absolute_url(self):
        return reverse('clientes:detail', kwargs={'pk': self.pk})
    
    def bonos_activos_count(self):
        """Cuenta los bonos activos del cliente"""
        return self.bonos.filter(activo=True).count()
    
    def bonos_agotados_count(self):
        """Cuenta los bonos agotados del cliente"""
        return self.bonos.filter(activo=False).count()
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos}"
