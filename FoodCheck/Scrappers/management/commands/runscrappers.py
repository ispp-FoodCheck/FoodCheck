from django.core.management.base import BaseCommand, CommandError
from Scrappers.mercadona import actualizar_datos_mercadona

class Command(BaseCommand):
    help = 'Actualiza los productos con los datos de Mercadona'

    def handle(self, *args, **options):
        actualizar_datos_mercadona()
        self.stdout.write(self.style.SUCCESS('Datos actualizados exitosamente'))