from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'email', 'telefono', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'apellidos', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'email', 'telefono', 'fecha_nacimiento')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
