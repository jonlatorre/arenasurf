from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clientes.models import Cliente
from django.db import transaction


class Command(BaseCommand):
    help = 'Limpiar problemas de usuarios y clientes duplicados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué cambios se harían sin aplicarlos',
        )
        parser.add_argument(
            '--fix-duplicates',
            action='store_true',
            help='Reparar usuarios/clientes duplicados',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        fix_duplicates = options.get('fix_duplicates', False)
        
        if dry_run:
            self.stdout.write('🔍 Modo DRY-RUN activado - No se realizarán cambios')
        
        self.stdout.write('=== DIAGNÓSTICO DE USUARIOS Y CLIENTES ===')
        
        # 1. Verificar usuarios sin cliente
        usuarios_sin_cliente = User.objects.filter(cliente__isnull=True).exclude(is_staff=True)
        self.stdout.write(f'👤 Usuarios sin cliente (no staff): {usuarios_sin_cliente.count()}')
        for user in usuarios_sin_cliente:
            self.stdout.write(f'  - {user.username} ({user.email})')
        
        # 2. Verificar clientes sin usuario
        clientes_sin_usuario = Cliente.objects.filter(usuario__isnull=True)
        self.stdout.write(f'👥 Clientes sin usuario: {clientes_sin_usuario.count()}')
        for cliente in clientes_sin_usuario:
            self.stdout.write(f'  - {cliente.nombre_completo} ({cliente.email})')
        
        # 3. Verificar emails duplicados en clientes
        from django.db.models import Count
        emails_duplicados = (Cliente.objects
                           .values('email')
                           .annotate(count=Count('email'))
                           .filter(count__gt=1))
        
        if emails_duplicados:
            self.stdout.write(f'📧 Emails duplicados en clientes: {emails_duplicados.count()}')
            for email_data in emails_duplicados:
                email = email_data['email']
                count = email_data['count']
                self.stdout.write(f'  - {email}: {count} clientes')
                clientes = Cliente.objects.filter(email=email)
                for cliente in clientes:
                    usuario_info = f" -> Usuario: {cliente.usuario.username}" if cliente.usuario else " -> Sin usuario"
                    self.stdout.write(f'    * {cliente.nombre_completo}{usuario_info}')
        
        # 4. Verificar usuarios con emails duplicados con clientes
        problemas_email = []
        for user in User.objects.all():
            clientes_con_email = Cliente.objects.filter(email=user.email)
            if clientes_con_email.count() > 1:
                problemas_email.append((user, clientes_con_email))
            elif clientes_con_email.count() == 1:
                cliente = clientes_con_email.first()
                if cliente.usuario != user:
                    problemas_email.append((user, clientes_con_email))
        
        if problemas_email:
            self.stdout.write(f'⚠️  Conflictos de email usuario-cliente: {len(problemas_email)}')
            for user, clientes in problemas_email:
                self.stdout.write(f'  - Usuario {user.username} ({user.email}):')
                for cliente in clientes:
                    usuario_info = f" vinculado a {cliente.usuario.username}" if cliente.usuario else " sin usuario"
                    self.stdout.write(f'    * Cliente {cliente.nombre_completo}{usuario_info}')
        
        # Reparaciones automáticas
        if fix_duplicates and not dry_run:
            self.stdout.write('\\n🔧 APLICANDO REPARACIONES...')
            
            with transaction.atomic():
                reparaciones = 0
                
                # Vincular usuarios con clientes por email
                for user in usuarios_sin_cliente:
                    clientes_matching = Cliente.objects.filter(email=user.email, usuario__isnull=True)
                    if clientes_matching.count() == 1:
                        cliente = clientes_matching.first()
                        cliente.usuario = user
                        cliente.save()
                        self.stdout.write(f'✅ Vinculado: {user.username} ↔ {cliente.nombre_completo}')
                        reparaciones += 1
                
                self.stdout.write(f'🎉 Reparaciones completadas: {reparaciones}')
        
        elif fix_duplicates and dry_run:
            self.stdout.write('\\n💡 Ejecuta sin --dry-run para aplicar las reparaciones')
        
        self.stdout.write('\\n✅ Diagnóstico completado')
