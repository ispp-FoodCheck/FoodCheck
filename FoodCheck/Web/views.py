from django.shortcuts import render
from .models import Producto
from random import randint

# Create your views here.

def index(request):
    lista_producto= Producto.objects.all()
    diccionario={'lista_producto':lista_producto}
    return render(request,"products.html",diccionario)

def shopping_list(request):
    #Ahora mismo muestra entre 8 productos aleatorios
    productos = set()
    for i in range(10):
        num_prods = Producto.objects.all().__len__()
        productos.add(Producto.objects.all()[randint(0, num_prods-1)])
    
    productos_agrupados_por_supermercado = {} #Diccionario que tiene como clave los supermercados y como valor un conjunto de productos que se vendan en ese supermercado

    for producto in productos:
        for supermercado in producto.supermercados.all():
            if productos_agrupados_por_supermercado.keys().__contains__(supermercado):
                productos_supermercado = productos_agrupados_por_supermercado[supermercado]
                productos_supermercado.add(producto)
                productos_agrupados_por_supermercado[supermercado] = productos_supermercado
            else:
                productos_agrupados_por_supermercado[supermercado] = set([producto])

    print(productos_agrupados_por_supermercado)
    
    return render(request,"shopping_list.html", {"productos_agrupados_por_supermercado":productos_agrupados_por_supermercado})
