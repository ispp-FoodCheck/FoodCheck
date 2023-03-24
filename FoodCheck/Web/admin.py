from django.contrib import admin
from .models import Alergeno, Supermercado, Producto, User, ListaCompra, Receta, Valoracion, RecetasDesbloqueadasUsuario, ReporteAlergenos

admin.site.register(Alergeno)
admin.site.register(Supermercado)
admin.site.register(Producto)
admin.site.register(User)
admin.site.register(ListaCompra)
admin.site.register(Receta)
admin.site.register(Valoracion)
admin.site.register(RecetasDesbloqueadasUsuario)
admin.site.register(ReporteAlergenos)