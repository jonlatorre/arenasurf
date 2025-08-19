from django.contrib import admin
from .models import Bono, UsoBono


class UsoBonoInline(admin.TabularInline):
    model = UsoBono
    extra = 0
    readonly_fields = ['fecha_uso']


@admin.register(Bono)
class BonoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_bono', 'usos_utilizados_display', 'usos_restantes', 'activo', 'fecha_compra']
    list_filter = ['tipo_bono', 'activo', 'fecha_compra']
    search_fields = ['cliente__nombre', 'cliente__apellidos', 'cliente__email']
    readonly_fields = ['fecha_compra', 'usos_totales']
    inlines = [UsoBonoInline]
    
    def usos_utilizados_display(self, obj):
        return f"{obj.usos_utilizados()}/{obj.usos_totales}"
    usos_utilizados_display.short_description = 'Usos'
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Bono', {
            'fields': ('tipo_bono', 'usos_totales', 'usos_restantes', 'precio')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_compra', 'fecha_expiracion')
        }),
    )


@admin.register(UsoBono)
class UsoBonoAdmin(admin.ModelAdmin):
    list_display = ['bono', 'fecha_uso', 'descripcion']
    list_filter = ['fecha_uso']
    search_fields = ['bono__cliente__nombre', 'bono__cliente__apellidos', 'descripcion']
    readonly_fields = ['fecha_uso']
