from datetime import date, timedelta
from random import randint

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe, require_POST, require_GET, require_http_methods
from unidecode import unidecode
from .forms import AllergenReportForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from .models import Alergeno, Producto, User, Valoracion, ListaCompra, ReporteAlergenos, Receta, RecetasDesbloqueadasUsuario
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
    valoraciones_con_comentario = Valoracion.objects.filter(producto=prod).exclude(comentario__isnull=True).all()
    ha_reportado = ReporteAlergenos.objects.filter(usuario=request.user, producto=prod).count() >= 1

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
            
    diccionario = {'producto':prod, 'valoraciones':valoraciones_con_comentario, 'ha_reportado': ha_reportado}
    return render(request, "product_details.html", diccionario)

@login_required(login_url='authentication:login')
def allergen_report(request, id_producto):
    
    formulario = AllergenReportForm()
    producto = Producto.objects.filter(id=id_producto)[0]
    alergenos = Alergeno.objects.all()

    if request.method == 'POST':
        formulario =AllergenReportForm(request.POST)
        if formulario.is_valid():
            usuario = request.user
            
            alergenos = [alergeno for alergeno in formulario.cleaned_data["allergens"]]
            for alergeno in alergenos:
                print(f'{alergeno.nombre} - {alergeno.id}')

            reporte = ReporteAlergenos.objects.create(usuario=usuario, producto=producto)
            reporte.alergenos.set(alergenos)
            reporte.save()

            return redirect(f'/product/{id_producto}/details')

    context = {
        'formulario': formulario,
        'alergenos': alergenos,
    }

    return render(request, 'allergen_report.html', context)

@require_safe
@login_required(login_url='authentication:login')
def shopping_list(request):
    productos = ListaCompra.objects.get(usuario = request.user).productos.all()
    print(len(productos))
    productos_agrupados_por_supermercado = {} #Diccionario que tiene como clave los supermercados y como valor un conjunto de productos que se vendan en ese supermercado

    for producto in productos:
        for supermercado in producto.supermercados.all():
            if supermercado in productos_agrupados_por_supermercado.keys():
                productos_supermercado = productos_agrupados_por_supermercado[supermercado]
                productos_supermercado.add(producto)
                productos_agrupados_por_supermercado[supermercado] = productos_supermercado
            else:
                productos_agrupados_por_supermercado[supermercado] = set([producto])

    return render(request,"shopping_list.html", {"productos_agrupados_por_supermercado":productos_agrupados_por_supermercado})

########### REPORTE DE ALERGENOS ###########
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser, login_url='admin:login', redirect_field_name=REDIRECT_FIELD_NAME)
def reports_list(request):
    reportes = ReporteAlergenos.objects.order_by('-fecha')

    context = {
        'reportes': reportes,
    }
    return render(request, 'reports_list.html', context)

@user_passes_test(is_superuser, login_url='admin:login', redirect_field_name=REDIRECT_FIELD_NAME)
def report_details(request, id_report):
    reporte = ReporteAlergenos.objects.filter(id=id_report)[0]

    # peticion aceptada
    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "aceptar":
            producto = Producto.objects.filter(id=reporte.producto.id)[0]
            producto.alergenos.add(*reporte.alergenos.all())
        reporte.delete()
        return redirect('/report/list')

    context = {
        'reporte': reporte,
    }
    return render(request, 'report_details.html', context)
    
@login_required(login_url='authentication:login')
@require_safe
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

@login_required(login_url='authentication:login')
@require_safe
def unlock_recipes(request):
    numero_pagina = request.POST.get('page') or 1
    lista_recetas_desbloquedas = RecetasDesbloqueadasUsuario.objects.filter(usuario=request.user)

    lista_recetas = []
    for receta_desbloquedas in lista_recetas_desbloquedas:
        if (request.user.premiumHasta != None and request.user.premiumHasta >= date.today()) or receta_desbloquedas.fechaBloqueo >= date.today():
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

@require_http_methods(["GET", "POST"])
def recipes_list(request):
    filtro_busqueda = request.POST.get('busqueda')
    numero_pagina = request.POST.get('page') or 1
    lista_recetas = Receta.objects.filter(publica=True)

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
@require_http_methods(["GET", "POST"])
def recipe_details(request, id_receta):

    receta = Receta.objects.filter(id=id_receta)[0]
    usuario = request.user
    receta_ya_desbloqueada = RecetasDesbloqueadasUsuario.objects.filter(usuario=usuario, receta=receta).exists()

    distinct_alergenos = set()
    for prod in receta.productos.all():
        for alergeno in prod.alergenos.all():
            distinct_alergenos.add(alergeno)

    ingredientes_visibles = False

    if((receta.propietario == usuario) or (receta_ya_desbloqueada and (RecetasDesbloqueadasUsuario.objects.filter(usuario=usuario, receta=receta)[0].fechaBloqueo >= date.today() or usuario.premiumHasta >= date.today()))):
        ingredientes_visibles = True

    puede_desbloquear = False
    
    if ingredientes_visibles==False and (usuario.recetaDiaria==None or usuario.recetaDiaria < date.today()) or (usuario.premiumHasta!=None and usuario.premiumHasta >= date.today()):
        puede_desbloquear = True

    context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}

    if request.method == "POST" and puede_desbloquear:
        usuario.recetaDiaria = date.today()
        usuario.save()
        #Sacar la fecha de dentro de una semana
        fecha_desbloqueo = date.today() + timedelta(days=7)
        RecetasDesbloqueadasUsuario.objects.create(usuario=usuario, receta=receta, fechaBloqueo=fecha_desbloqueo)
        ingredientes_visibles = True
        context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}

    if request.method == "POST" and usuario==receta.propietario and receta.publica==False:
        receta.publica = True
        receta.save()
        context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}

    return render(request, "recipe_details.html", context)

@login_required(login_url='authentication:login')
@require_http_methods(["GET", "POST"])
def new_recipes(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('cuerpo')
        tiempo_horas = request.POST.get('horas')
        tiempo_minutos = request.POST.get('minutos')
        tiempo_segundos = request.POST.get('segundos')
        publica = request.POST.get('checkbox_publica')
        img = request.FILES.get('receta_imagen')

        productos_escogidos = request.POST.getlist('productos[]') #recoge las id en formato lista

        if publica == "si": 
            publica=True
        else:
            publica=False

        propietario = request.user

        # El tiempo de preparación se guarda como campo de texto (solo se usa para visualizar)
        tiempo_preparacion = str(tiempo_horas) + " horas, " + str(tiempo_minutos) + " minutos, " + str(tiempo_segundos) + " segundos "

        receta = Receta.objects.create(
                nombre=nombre, descripcion=descripcion, tiempoPreparacion=tiempo_preparacion,
                  publica=publica, propietario=propietario, imagen=img)
        receta.productos.set(productos_escogidos) #se setea la lista de productos
        receta.save()

        return redirect('/my_recipes/')

    return render(request, "new_recipe.html", context)

@require_safe
def add_product(request, id_producto):

    lista_compra = ListaCompra.objects.filter(usuario = request.user).all()
    producto_a_añadir = Producto.objects.get(id__exact = id_producto)

    if len(lista_compra) == 0:
        lista_compra = ListaCompra(usuario = request.user)
        lista_compra.save()
    else:
        lista_compra = lista_compra[0]


    if len(lista_compra.productos.all()) != 0:
        lista_compra.productos.add(producto_a_añadir)
    else:
        lista_compra.productos.set([producto_a_añadir])

    lista_compra.save()

    return shopping_list(request)

@require_safe
def remove_product(request, id_producto):

    lista_compra = ListaCompra.objects.get(usuario = request.user)
    producto_a_quitar = Producto.objects.get(id__exact = id_producto)

    if lista_compra is not None:
        lista_compra.productos.remove(producto_a_quitar)
        lista_compra.save()

    return shopping_list(request)
