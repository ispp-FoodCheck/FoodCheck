from django.shortcuts import render
from random import randint
from django.core.paginator import Paginator
from .models import Producto, Valoracion, Usuario, Alergeno
from django.views.decorators.http import require_safe, require_http_methods
from django.db.models.functions import Lower
from unidecode import unidecode
# Create your views here.

def landing_page(request):
    context = {

    }
    return render(request, "landing.html", context)

def index(request):
    alergenos_selected = request.GET.getlist('alergenos')
    alergenos = Alergeno.objects.exclude(imagen__isnull=True)
    palabra_buscador = request.GET.get('canal_de_texto')

    if request.user.is_authenticated and alergenos_selected == None:
        alergenos_selected = list(request.user.alergenos.all())

    lista_producto = Producto.objects.exclude(alergenos__nombre__in=alergenos_selected)

    if request.GET.get('vegano'):
        lista_producto = lista_producto.filter(vegano=True)
        vegano_selected = True
    else:
        vegano_selected = False
    
    if palabra_buscador != None:
        lista_producto= lista_producto.annotate(nombre_m=Lower('nombre')).filter(nombre_m__icontains=unidecode(palabra_buscador.lower()))

    paginacion= Paginator(lista_producto,12)
    total_de_paginas= paginacion.num_pages
    numero_pagina= request.GET.get('page')
    objetos_de_la_pagina= paginacion.get_page(numero_pagina)
    diccionario={'lista_producto':objetos_de_la_pagina,'alergenos_available':alergenos,'alergenos_selected':alergenos_selected,'vegano_selected':vegano_selected, 'total_de_paginas': total_de_paginas}
    return render(request,"products.html",diccionario)

def product_details(request, id_producto):
    diccionario = {}
    prod = Producto.objects.filter(id=id_producto)[0]
    valoraciones_con_comentario = Valoracion.objects.filter(producto=prod).exclude(comentario__isnull=True).all()

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

            valoraciones = Valoracion.objects.filter(producto=prod).all()
            puntuaciones = [v.puntuacion for v in valoraciones]
            puntuaciones.append(int(puntuacion))
            media = sum(puntuaciones) / len(puntuaciones)
            prod.valoracionMedia = media
            prod.save()
            
    diccionario = {'producto':prod, 'valoraciones':valoraciones_con_comentario}
    return render(request, "product_details.html", diccionario)

@require_safe
def shopping_list(request):
    # Ahora mismo muestra entre 8 productos aleatorios
    productos = set()
    for i in range(10):
        num_prods = len(Producto.objects.all())
        productos.add(Producto.objects.all()[randint(0, num_prods-1)])

    productos_agrupados_por_supermercado = {} #Diccionario que tiene como clave los supermercados y como valor un conjunto de productos que se vendan en ese supermercado

    for producto in productos:
        for supermercado in producto.supermercados.all():
            if supermercado in productos_agrupados_por_supermercado.keys():
                productos_supermercado = productos_agrupados_por_supermercado[supermercado]
                productos_supermercado.add(producto)
                productos_agrupados_por_supermercado[supermercado] = productos_supermercado
            else:
                productos_agrupados_por_supermercado[supermercado] = set([producto])
    print(productos_agrupados_por_supermercado)

    return render(request,"shopping_list.html", {"productos_agrupados_por_supermercado":productos_agrupados_por_supermercado})