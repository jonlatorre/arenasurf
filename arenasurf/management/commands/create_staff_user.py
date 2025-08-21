from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Crear un usuario staff para gestionar las aplicaciones de Arena Surf'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario para el staff',
            required=True,
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del usuario staff',
            required=True,
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña del usuario (opcional, si no se proporciona se pedirá)',
            required=False,
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Crear como superusuario en lugar de solo staff',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        is_superuser = options.get('superuser', False)

        # Si no se proporciona contraseña, pedirla
        if not password:
            import getpass
            password = getpass.getpass('Introduzca la contraseña: ')

        try:
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    f'✅ Superusuario "{username}" creado correctamente.'
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.is_staff = True
                user.save()
                self.stdout.write(
                    f'✅ Usuario staff "{username}" creado correctamente.'
                )

        except IntegrityError:
            self.stdout.write(
                f'❌ Error: El usuario "{username}" ya existe.'
            )
        except ValueError as e:
            self.stdout.write(
                f'❌ Error en los datos proporcionados: {str(e)}'
            )
