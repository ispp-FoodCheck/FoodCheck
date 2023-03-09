from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Producto, Valoracion, Usuario, Alergeno

# Create your views here.

def index(request):
    alergenos_selected = request.GET.getlist('alergenos')
    alergenos = Alergeno.objects.exclude(imagen__isnull=True)

    if request.user.is_authenticated and alergenos_selected == None:
        alergenos_selected = list(request.user.alergenos.all())

    lista_producto = Producto.objects.exclude(alergenos__nombre__in=alergenos_selected)

    if request.GET.get('vegano'):
        lista_producto = lista_producto.filter(vegano=True)
        vegano_selected = True
    else:
        vegano_selected = False
    
    paginacion= Paginator(lista_producto,12)
    numero_pagina= request.GET.get('page')
    objetos_de_la_pagina= paginacion.get_page(numero_pagina)
    diccionario={'lista_producto':objetos_de_la_pagina,'alergenos_available':alergenos,'alergenos_selected':alergenos_selected,'vegano_selected':vegano_selected}
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
