from django.core.management.base import BaseCommand, CommandError
from Scrappers.mercadona import actualizar_datos_mercadona
from Scrappers.carrefour import main as actualizar_datos_carrefour

class Command(BaseCommand):
    help = 'Actualiza los productos con los datos de Mercadona'

    def handle(self, *args, **options):
        actualizar_datos_mercadona()
        actualizar_datos_carrefour()
        self.stdout.write(self.style.SUCCESS('Datos actualizados exitosamente'))