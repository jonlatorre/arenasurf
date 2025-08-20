from django.contrib import admin
from .models import Socio


@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = [
        'numero_socio', 'cliente', 'nivel', 'esta_vigente', 
        'fecha_vencimiento', 'numero_taquilla', 'numero_guardatablas',
        'precio_anual', 'activo'
    ]
    list_filter = ['nivel', 'activo', 'fecha_vencimiento', 'created_at']
    search_fields = [
        'numero_socio', 'cliente__nombre', 'cliente__apellidos', 
        'cliente__email', 'numero_taquilla', 'numero_guardatablas'
    ]
    list_editable = ['activo']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'numero_socio', 'nivel', 'activo')
        }),
        ('Membresía', {
            'fields': ('fecha_alta', 'fecha_vencimiento', 'precio_anual')
        }),
        ('Servicios', {
            'fields': ('numero_taquilla', 'numero_guardatablas')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def esta_vigente(self, obj):
        return obj.esta_vigente
    esta_vigente.boolean = True
    esta_vigente.short_description = 'Vigente'
