from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clientes.models import Cliente


class Command(BaseCommand):
    help = 'Vincular usuarios existentes con clientes por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué cambios se harían sin aplicarlos',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write('🔍 Modo DRY-RUN activado - No se realizarán cambios')
        
        # Buscar clientes sin usuario asociado
        clientes_sin_usuario = Cliente.objects.filter(usuario__isnull=True)
        self.stdout.write(f'📊 Encontrados {clientes_sin_usuario.count()} clientes sin usuario asociado')
        
        vinculaciones = 0
        
        for cliente in clientes_sin_usuario:
            try:
                # Buscar usuario con el mismo email
                usuario = User.objects.get(email=cliente.email)
                
                # Verificar que el usuario no esté ya vinculado a otro cliente
                if hasattr(usuario, 'cliente') and usuario.cliente != cliente:
                    self.stdout.write(
                        f'⚠️  Usuario {usuario.username} ya está vinculado a otro cliente'
                    )
                    continue
                
                if dry_run:
                    self.stdout.write(
                        f'🔗 Se vincularía: {cliente.nombre_completo} ↔ {usuario.username}'
                    )
                else:
                    cliente.usuario = usuario
                    cliente.save()
                    self.stdout.write(
                        f'✅ Vinculado: {cliente.nombre_completo} ↔ {usuario.username}'
                    )
                
                vinculaciones += 1
                
            except User.DoesNotExist:
                self.stdout.write(
                    f'❌ No se encontró usuario con email: {cliente.email}'
                )
            except User.MultipleObjectsReturned:
                self.stdout.write(
                    f'⚠️  Múltiples usuarios con email: {cliente.email}'
                )
        
        if dry_run:
            self.stdout.write(f'📈 Se vincularían {vinculaciones} clientes')
            self.stdout.write('💡 Ejecuta sin --dry-run para aplicar los cambios')
        else:
            self.stdout.write(f'🎉 Proceso completado: {vinculaciones} clientes vinculados')
