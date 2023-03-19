from random import randint

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import render
from django.views.decorators.http import require_safe
from unidecode import unidecode

from .models import Alergeno, Producto, User, Valoracion, Receta, RecetasDesbloqueadasUsuario

# Create your views here.


def landing_page(request):
    context = {

    }
    return render(request, "landing.html", context)


def index(request):
    vegano_selected = False
    numero_pagina = request.POST.get('page') or 1
    alergenos_selected = request.POST.getlist('alergenos_selected')
    alergenos = Alergeno.objects.exclude(imagen__isnull=True)
    palabra_buscador = request.POST.get('canal_de_texto') or ''
    print(alergenos_selected)

    if request.user.is_authenticated and len(alergenos_selected) == 0 and request.method == 'GET':
        alergenos_selected = list(
            request.user.alergenos.all().values_list('nombre', flat=True))
        if request.user.es_vegano:
            vegano_selected = True

    lista_producto = Producto.objects.exclude(
        alergenos__nombre__in=alergenos_selected)

    if request.POST.get('vegano') == '1':
        lista_producto = lista_producto.filter(vegano=True)
        vegano_selected = True

    if palabra_buscador != None:
        lista_producto = lista_producto.annotate(nombre_m=Lower('nombre')).filter(
            nombre_m__icontains=unidecode(palabra_buscador.lower()))

    paginacion = Paginator(lista_producto, 12)
    total_de_paginas = paginacion.num_pages

    objetos_de_la_pagina = paginacion.get_page(numero_pagina)
    diccionario = {'lista_producto': objetos_de_la_pagina, 'alergenos_available': alergenos, 'alergenos_selected': alergenos_selected,
                   'vegano_selected': vegano_selected, 'total_de_paginas': total_de_paginas, 'palabra_buscador': palabra_buscador}
    return render(request, "products.html", diccionario)


@login_required(login_url='authentication:login')
def product_details(request, id_producto):
    diccionario = {}
    prod = Producto.objects.filter(id=id_producto)[0]
    valoraciones_con_comentario = Valoracion.objects.filter(
        producto=prod).exclude(comentario__isnull=True).all()

    # form valoracion
    if request.method == 'POST':
        comentario = request.POST.get('cuerpo')
        if (comentario == ''):
            comentario = None
        puntuacion = request.POST.get('valoracion')

        if (puntuacion != ''):
            usuario = request.user
            valoracion = Valoracion.objects.create(
                comentario=comentario, puntuacion=puntuacion, usuario=usuario, producto=prod)
            valoracion.save()

            valoraciones = Valoracion.objects.filter(producto=prod).all()
            puntuaciones = [v.puntuacion for v in valoraciones]
            puntuaciones.append(int(puntuacion))
            media = sum(puntuaciones) / len(puntuaciones)
            prod.valoracionMedia = media
            prod.save()

    diccionario = {'producto': prod,
                   'valoraciones': valoraciones_con_comentario}
    return render(request, "product_details.html", diccionario)


@require_safe
def shopping_list(request):
    # Ahora mismo muestra entre 8 productos aleatorios
    productos = set()
    for i in range(10):
        num_prods = len(Producto.objects.all())
        productos.add(Producto.objects.all()[randint(0, num_prods-1)])

    # Diccionario que tiene como clave los supermercados y como valor un conjunto de productos que se vendan en ese supermercado
    productos_agrupados_por_supermercado = {}

    for producto in productos:
        for supermercado in producto.supermercados.all():
            if supermercado in productos_agrupados_por_supermercado.keys():
                productos_supermercado = productos_agrupados_por_supermercado[supermercado]
                productos_supermercado.add(producto)
                productos_agrupados_por_supermercado[supermercado] = productos_supermercado
            else:
                productos_agrupados_por_supermercado[supermercado] = set([
                                                                         producto])
    print(productos_agrupados_por_supermercado)

    return render(request, "shopping_list.html", {"productos_agrupados_por_supermercado": productos_agrupados_por_supermercado})

def my_recipes(request):
    numero_pagina = request.POST.get('page') or 1
    lista_recetas = Receta.objects.filter(propietario=request.user)

    diccionario_recetas_alergenos = dict()

    for receta in lista_recetas:
        distinct_alergenos = set()
        for prod in receta.productos.all():
            for alergeno in prod.alergenos.all():
                distinct_alergenos.add(alergeno)
        diccionario_recetas_alergenos[receta] = distinct_alergenos

    paginacion = Paginator(lista_recetas, 12)
    total_de_paginas = paginacion.num_pages

    objetos_de_la_pagina = paginacion.get_page(numero_pagina)

    context = {'lista_producto': objetos_de_la_pagina,
               'total_de_paginas': total_de_paginas,
               'recetas': diccionario_recetas_alergenos}

    return render(request, "my_recipes.html", context)

def unlock_recipes(request):
    numero_pagina = request.POST.get('page') or 1
    lista_recetas_desbloquedas = RecetasDesbloqueadasUsuario.objects.filter(usuario=request.user)

    lista_recetas = []
    for receta_desbloquedas in lista_recetas_desbloquedas:
        lista_recetas.append(receta_desbloquedas.receta)
    
    diccionario_recetas_alergenos = dict()

    for receta in lista_recetas:
        distinct_alergenos = set()
        for prod in receta.productos.all():
            for alergeno in prod.alergenos.all():
                distinct_alergenos.add(alergeno)
        diccionario_recetas_alergenos[receta] = distinct_alergenos

    paginacion = Paginator(lista_recetas, 12)
    total_de_paginas = paginacion.num_pages

    objetos_de_la_pagina = paginacion.get_page(numero_pagina)

    context = {'lista_producto': objetos_de_la_pagina,
               'total_de_paginas': total_de_paginas,
               'recetas': diccionario_recetas_alergenos}

    return render(request, "unlock_recipes.html", context)

def recipes_list(request):
    filtro_busqueda = request.POST.get('busqueda')
    numero_pagina = request.POST.get('page') or 1
    lista_recetas = Receta.objects.all()

    if filtro_busqueda != None:
        lista_recetas = lista_recetas.annotate(nombre_m=Lower('nombre')).filter(
            nombre_m__icontains=unidecode(filtro_busqueda.lower()))

    diccionario_recetas_alergenos = dict()

    for receta in lista_recetas:
        distinct_alergenos = set()
        for prod in receta.productos.all():
            for alergeno in prod.alergenos.all():
                distinct_alergenos.add(alergeno)
        diccionario_recetas_alergenos[receta] = distinct_alergenos


    paginacion = Paginator(lista_recetas, 12)
    total_de_paginas = paginacion.num_pages

    objetos_de_la_pagina = paginacion.get_page(numero_pagina)

    context = {'lista_producto': objetos_de_la_pagina,
               'total_de_paginas': total_de_paginas,
               'recetas': diccionario_recetas_alergenos,
               'filtro_productos': filtro_busqueda}

    return render(request, "recipes.html", context)

@login_required(login_url='authentication:login')
def recipe_details(request, id_receta):
    receta = Receta.objects.filter(id=id_receta)[0]

    distinct_alergenos = set()
    for prod in receta.productos.all():
        for alergeno in prod.alergenos.all():
            distinct_alergenos.add(alergeno)

    context = {'receta': receta, 'alergenos': distinct_alergenos}

    return render(request, "recipe_details.html", context)

def new_recipes(request):

    context = {

    }
    return render(request, "landing.html", context)
