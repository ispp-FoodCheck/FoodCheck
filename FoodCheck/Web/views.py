from django.shortcuts import render
from .models import Producto, Valoracion, Usuario

# Create your views here.

def index(request):
    lista_producto= Producto.objects.all()
    diccionario={'lista_producto':lista_producto}
    return render(request,"products.html",diccionario)

def product_details(request, id_producto):
    diccionario = {}
    prod = Producto.objects.filter(id=id_producto)[0]
    
    # form valoracion
    if request.method == 'POST':
        comentario = request.POST.get('cuerpo')
        if (comentario == ''):
            comentario = None
        puntuacion = request.POST.get('valoracion')

        if (puntuacion != ''):
            usuario = Usuario.objects.filter(id=1)[0]
            valoracion = Valoracion.objects.create(comentario=comentario, puntuacion=puntuacion, usuario=usuario, producto=prod)
            valoracion.save()

    valoraciones = Valoracion.objects.filter(producto=prod).exclude(comentario__isnull=True).all()
    
    diccionario = {'producto':prod, 'valoraciones':valoraciones}
    return render(request, "product_details.html", diccionario)