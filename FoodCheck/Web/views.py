from datetime import date, timedelta
from django.shortcuts import render, redirect, HttpResponse

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_safe, require_http_methods
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from unidecode import unidecode
from .forms import AllergenReportForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from .models import Alergeno, Producto, Valoracion, ListaCompra, ReporteAlergenos, Receta, RecetasDesbloqueadasUsuario, ListaCompra, Producto, Supermercado
from django.http import JsonResponse
from django.core import serializers
import json
from django.db.models import Avg

from spanlp.palabrota import Palabrota
from payments.utils import es_premium

# Create your views here.
@require_safe

def landing_page(request):
    context = {

    }
    return render(request, "landing.html", context)

@require_http_methods(["GET", "POST"])
def index(request):
    vegano_selected = False
    numero_pagina = request.POST.get('page') or 1
    alergenos_selected = request.POST.getlist('alergenos_selected')
    alergenos = Alergeno.objects.exclude(imagen__isnull=True)
    supermercados = Supermercado.objects.all()
    supermercados_selected = request.POST.getlist('supermercados_selected')
    palabra_buscador = request.POST.get('canal_de_texto') or ''
    

    if request.user.is_authenticated:
        es_premium(request.user)

    if request.user.is_authenticated and len(alergenos_selected) == 0 and request.method == 'GET':
        alergenos_selected = list(
            request.user.alergenos.all().values_list('nombre', flat=True))
        if request.user.es_vegano:
            vegano_selected = True
            
    lista_producto = Producto.objects.exclude(alergenos__nombre__in=alergenos_selected)        
    
    if len(supermercados_selected) != 0:
        lista_producto = Producto.objects.exclude(alergenos__nombre__in=alergenos_selected).filter(supermercados__nombre__in=supermercados_selected)     
            
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
                   'vegano_selected': vegano_selected, 'total_de_paginas': total_de_paginas, 'palabra_buscador': palabra_buscador, 'supermercados':supermercados, 'supermercados_selected':supermercados_selected}
    return render(request, "products.html", diccionario)


@login_required(login_url='authentication:login')
def product_details(request, id_producto):
    if request.user.is_authenticated:
        es_premium(request.user)

    diccionario = {}
    prod = Producto.objects.filter(id=id_producto)[0]
    valoraciones_con_comentario = Valoracion.objects.filter(producto=prod).exclude(comentario__isnull=True).all()
    ha_reportado = ReporteAlergenos.objects.filter(usuario=request.user, producto=prod).count() >= 1
    
    lista_recetas = Receta.objects.filter(productos__id=id_producto)
    diccionario_recetas_alergenos = dict()

    for receta in lista_recetas:
        distinct_alergenos = set()
        for productoReceta in receta.productos.all():
            for alergeno in productoReceta.alergenos.all():
                distinct_alergenos.add(alergeno)
        diccionario_recetas_alergenos[receta] = distinct_alergenos

    valoraciones_user = Valoracion.objects.filter(producto=prod,usuario=request.user).all()
    
    # form valoracion
    if request.method == 'POST':
        comentario = request.POST.get('cuerpo')
        if (comentario == ''):
            comentario = None

        palabrota = Palabrota(censor_char="*")

        comentario = palabrota.censor(input_text=comentario)

        
        puntuacion = request.POST.get('valoracion')


        if (puntuacion != '' and len(valoraciones_user)<1):
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

            valoraciones_user = Valoracion.objects.filter(producto=prod,usuario=request.user).all()
            
    diccionario = {'producto':prod, 'valoraciones':valoraciones_con_comentario, 'ha_reportado': ha_reportado, 'recetas':diccionario_recetas_alergenos, 'n_valoraciones':len(valoraciones_user)}
    return render(request, "product_details.html", diccionario)





@login_required(login_url='authentication:login')
def allergen_report(request, id_producto):
   
    formulario = AllergenReportForm()
    producto = Producto.objects.filter(id=id_producto)[0]
    alergenos = Alergeno.objects.filter(imagen__isnull=False)

    if request.method == 'POST':
        formulario = AllergenReportForm(request.POST)
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
        'producto': producto
    }

    return render(request, 'allergen_report.html', context)

@require_safe
@login_required(login_url='authentication:login')
def shopping_list(request):
    lista_compra = ListaCompra.objects.filter(usuario=request.user)
    if(lista_compra.exists()==False):
                ListaCompra.objects.create(usuario=request.user)
                lista_compra = ListaCompra.objects.filter(usuario=request.user)
    productos = lista_compra.get().productos.all()
    productos_agrupados_por_supermercado = {} #Diccionario que tiene como clave los supermercados y como valor un conjunto de productos que se vendan en ese supermercado

    for producto in productos:
        for supermercado in producto.supermercados.all():
            if supermercado in productos_agrupados_por_supermercado.keys():
                productos_supermercado = productos_agrupados_por_supermercado[supermercado]
                productos_supermercado.add(producto)
                productos_agrupados_por_supermercado[supermercado] = productos_supermercado
            else:
                productos_agrupados_por_supermercado[supermercado] = set([producto])
    
    # Obtener el número de productos por supermercado
    num_productos_por_supermercado = {}
    for supermercado, productos in productos_agrupados_por_supermercado.items():
        num_productos = len(productos)
        num_productos_por_supermercado[supermercado] = num_productos


    return render(request,"shopping_list.html", {"productos_agrupados_por_supermercado":productos_agrupados_por_supermercado, "num_productos_por_supermercado":num_productos_por_supermercado})

@require_safe
@login_required(login_url='authentication:login')
def premium(request):
    if request.user.is_authenticated:
        es_premium(request.user)

    return render(request,"premium.html")

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
            user = reporte.usuario
            user.premiumHasta = date.today() + timedelta(days=7)
            user.save()
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
    if request.user.is_authenticated:
        es_premium(request.user)

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
@login_required(login_url='authentication:login')
def recipes_list(request):
    filtro_busqueda = request.POST.get('busqueda')
    numero_pagina = request.POST.get('page') or 1
    lista_recetas = Receta.objects.filter(publica=True)
    filtro_busqueda_id_productos = request.POST.getlist('productos[]')
    productos_filtrados = Producto.objects.filter(id__in=filtro_busqueda_id_productos)
    message = None
    
    if filtro_busqueda != None:
        lista_recetas = lista_recetas.annotate(nombre_m=Lower('nombre')).filter(
            nombre_m__icontains=unidecode(filtro_busqueda.lower()))
        
    if len(filtro_busqueda_id_productos)>0  :
        if request.user.premiumHasta != None and request.user.premiumHasta >= date.today():
            lista_recetas = list(filter(lambda receta: all(str(id) in [str(producto.id) for producto in receta.productos.all()] for id in filtro_busqueda_id_productos), lista_recetas))
        else:
            message = 'La funcionalidad de filtrar por productos es solo para usuarios premium'            
    
        
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
               'filtro_productos': filtro_busqueda,
               'productos_selec': productos_filtrados,
               'solo_premium':message}

    return render(request, "recipes.html", context)

@login_required(login_url='authentication:login')
@require_http_methods(["GET", "POST"])
def recipe_details(request, id_receta):


    receta = Receta.objects.filter(id=id_receta)[0]
    usuario = request.user
    
    if request.user.is_authenticated:
        es_premium(request.user)

    receta_ya_desbloqueada = RecetasDesbloqueadasUsuario.objects.filter(usuario=usuario, receta=receta).exists()

    distinct_alergenos = set()
    for prod in receta.productos.all():
        for alergeno in prod.alergenos.all():
            distinct_alergenos.add(alergeno)

    ingredientes_visibles = False

    if((receta.propietario == usuario) or (receta_ya_desbloqueada and (RecetasDesbloqueadasUsuario.objects.filter(usuario=usuario, receta=receta)[0].fechaBloqueo >= date.today() or usuario.premiumHasta!=None and usuario.premiumHasta>= date.today()))):
        ingredientes_visibles = True

    puede_desbloquear = False
    
    if ingredientes_visibles==False and (usuario.recetaDiaria==None or usuario.recetaDiaria < date.today()) or (usuario.premiumHasta!=None and usuario.premiumHasta >= date.today()):
        puede_desbloquear = True

    context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}

    if(request.method == "POST"):
        if("desbloqueo" in request.POST and puede_desbloquear):
            usuario.recetaDiaria = date.today()
            usuario.save()
            #Sacar la fecha de dentro de una semana
            fecha_desbloqueo = date.today() + timedelta(days=7)
            receta_desbloqueada = RecetasDesbloqueadasUsuario.objects.filter(usuario=usuario, receta=receta)
            if(receta_desbloqueada.exists()==False):
                receta_desbloqueada = RecetasDesbloqueadasUsuario(usuario=usuario, receta=receta, fechaBloqueo=fecha_desbloqueo)
                receta_desbloqueada.save()
            else:
                relacion = receta_desbloqueada.get()
                relacion.fechaBloqueo = fecha_desbloqueo
                relacion.save()
            ingredientes_visibles = True
            context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}

        elif("publicar" in request.POST and receta.propietario==usuario and receta.publica==False):
            receta.publica = True
            receta.save()
            context = {'receta': receta, 'alergenos': distinct_alergenos, 'visible': ingredientes_visibles, 'desbloqueado_disponible': puede_desbloquear, 'puede_publicar': receta.propietario==usuario and receta.publica==False}
        
        elif("añadir-productos" in request.POST and ingredientes_visibles):
            lista_compra_usuario = ListaCompra.objects.filter(usuario=usuario)
            if(lista_compra_usuario.exists()==False):
                ListaCompra.objects.create(usuario=usuario)
                lista_compra_usuario = ListaCompra.objects.filter(usuario=usuario)
            for producto in receta.productos.all():
                lista_compra_usuario[0].productos.add(producto)
            lista_compra_usuario[0].save()

            return redirect('/shopping_list/')

    return render(request, "recipe_details.html", context)

@login_required(login_url='authentication:login')
@require_http_methods(["GET", "POST"])
def new_recipes(request):
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

        if len(productos_escogidos) < 2:
            messages.error(request,"Para crear una nueva receta debe añadir al menos dos ingredientes.")
            return redirect('new_recipes')

        propietario = request.user

        # El tiempo de preparación se guarda como campo de texto (solo se usa para visualizar)
        tiempo_preparacion = str(tiempo_horas) + " horas, " + str(tiempo_minutos) + " minutos, " + str(tiempo_segundos) + " segundos "

        receta = Receta.objects.create(
                nombre=nombre, descripcion=descripcion, tiempoPreparacion=tiempo_preparacion,
                  publica=publica, propietario=propietario, imagen=img)
        receta.productos.set(productos_escogidos) #se setea la lista de productos
        receta.save()

        return redirect('/my_recipes/')

    return render(request, "new_recipe.html")

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

@require_safe
def get_products_endpoint(request):
    if request.GET.get('nombre'):
        productos = Producto.objects.annotate(nombre_m=Lower('nombre')).filter(nombre_m__icontains=unidecode(request.GET.get('nombre').lower()))[:10]
    else:
        productos = []
    data = json.dumps(list(map(lambda x: (x.id, x.nombre, x.imagen), productos)))
    return HttpResponse(data, content_type='application/json')


@login_required
def delete_valoracion(request, valoracion_id):
    valoracion = get_object_or_404(Valoracion, id=valoracion_id)
    post_id = ""
    if request.method == 'POST':
        if request.user == valoracion.usuario:
            post_id = valoracion.producto.id
            valoracion.delete()
            producto = Producto.objects.get(pk=post_id)
            producto.actualizar_valoracion_media()
            messages.success(request, 'Valoracion deleted successfully.')
            return redirect('product_details', id_producto=post_id)
        else:
            messages.error(request, 'You are not authorized to delete this valoracion.')
            return redirect('product_details', id_producto=post_id)
    else:
        return redirect('product_details', id_producto=post_id)

@require_safe
def trending_productos(request):
    productos = sorted(Producto.objects.all(), key=lambda p: p.get_popularity(), reverse=True)[0:5]
    productos = [(p, 100*p.valoracionMedia/p.get_popularity()) for p in productos]
    return render(request, "trending_productos.html", {'products':productos})
    

