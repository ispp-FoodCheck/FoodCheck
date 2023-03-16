import re
from urllib.request import urlopen
import json
import sys
from Web.models import Producto, Supermercado, Alergeno
from Scrappers.alergenos import MAPA_INTOLERANCIAS_CARREFOUR, obtener_alergenos_de_texto

num_elementos = '20'

url_keywords = "https://www.carrefour.es/search-api/suggestions/v1/empathize?lang=es&catalog=food&rows=" + num_elementos


def find_keywords():

    trending = set()

    # Realizamos la solicitud HTTP a la página de Carrefour
    response = urlopen(url_keywords)
    # Leemos el contenido de la respuesta HTTP
    content = response.read()

    # Cerramos la conexión
    response.close()

    # Analizamos el contenido JSON de la respuesta
    data = json.loads(content)

    trends = data['topTrends']

    for trend in trends:
        trending.add(trend['title_raw'].replace(' ', '_'))

    return trending


def search_products(keyword):
    url_search = "https://www.carrefour.es/search-api/query/v1/search?lang=es&query=" + keyword + "&rows=" + num_elementos
    # Realizamos la solicitud HTTP a la página de Carrefour
    response = urlopen(url_search)

    # Leemos el contenido de la respuesta HTTP
    content = response.read()

    # Cerramos la conexión
    response.close()

    # Analizamos el contenido JSON de la respuesta
    data = json.loads(content)

    # Imprimimos todos los nombres de producto encontrados
    docs = data['content']["docs"]

    product_ids = set()

    for product in docs:
        product_ids.add(product['product_id'])

    return product_ids


def product_details(product_id):
    url_product = "https://www.carrefour.es/cloud-api/pdp-food/v1?product_id=" + product_id
    # Realizamos la solicitud HTTP a la página de Carrefour
    response = urlopen(url_product)
    # Leemos el contenido de la respuesta HTTP
    content = response.read()
    # Cerramos la conexión
    response.close()
    # Analizamos el contenido JSON de la respuesta
    data = json.loads(content)

    try:
        data['product']
    except KeyError:
        return 0

    product = data['product']

    try:
        nombre = product['name'][:100]
    except KeyError:
        nombre = '-'
    try:
        ean = product['ean']
    except KeyError:
        ean = '-'
    try:
        imagen = product['images'][0]['medium']
    except KeyError:
        imagen = '-'
    try:
        marca = product['brand']['description']
    except KeyError:
        marca = 'Desconocida'
    try:
        alergenos = product['nutrition_info']['alergenos']['contiene']
    except KeyError:
        alergenos = '-'
    try:
        ingredientes = re.sub(
            r'<\/?\w+>', '', product['nutrition_info']['ingredientes'])[:2000]
    except KeyError:
        ingredientes = 'Sin ingredientes'

    return {
        'id': product_id,
        'ean': ean,
        'nombre': nombre,
        'imagen': imagen,
        'marca': marca,
        'ingredientes': ingredientes,
        'alergenos': alergenos,
        'vegano': True
    }


def update_progress(progress, total, bar_length=20):
    
    # calcular el porcentaje completado
    percent = "{0:.1f}".format(100 * (progress / float(total)))
    # calcular el número de símbolos a mostrar
    filled_length = int(round(bar_length * progress / float(total)))
    # crear la barra de progreso con símbolos #
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    # imprimir la barra de progreso con el porcentaje y un retorno de carro
    sys.stdout.write('\r[%s] %s%%' % (bar, percent))
    sys.stdout.flush()  # limpiar el buffer


def actualizar_datos_carrefour():
    try:
        carrefour = Supermercado.objects.get(id=2)
    except Supermercado.DoesNotExist:
        carrefour = Supermercado.objects.create(
            id=2, nombre='Carrefour', foto='https://1000marcas.net/wp-content/uploads/2020/11/Carrefour-Logo.png')

    keywords = find_keywords()

    products_ids = []

    for keyword in keywords:
        products_ids.extend(search_products(keyword))

    iteration = 1
    for product_id in products_ids:
        update_progress(iteration, len(products_ids))
        detailed_product = product_details(product_id)
        if isinstance(detailed_product, int):
            continue
        
        producto, created = Producto.objects.get_or_create(id=int(detailed_product['ean']), defaults={
                'nombre': detailed_product['nombre'],
                'imagen': detailed_product['imagen'],
                'ingredientes': detailed_product['ingredientes'],
                'marca': detailed_product['marca']
            })
        if created:
            producto.supermercados.set([carrefour])
        else:
            producto.nombre = detailed_product['nombre']
            producto.imagen = detailed_product['imagen']
            producto.ingredientes = detailed_product['ingredientes']
            producto.marca = detailed_product['marca']
            if carrefour not in producto.supermercados.all():
                producto.supermercados.add(carrefour)
        producto.save()
        
        alergenos = obtener_alergenos_de_texto(detailed_product['nombre'])
        alergenos.extend(obtener_alergenos_de_texto(detailed_product['ingredientes']))
        alergenos = set(alergenos)
        for i in detailed_product['alergenos'].split(", "):
            if i== '-':
                break
            alergeno = None
            if i in MAPA_INTOLERANCIAS_CARREFOUR.keys():
                alergeno = Alergeno.objects.get_or_create(nombre=MAPA_INTOLERANCIAS_CARREFOUR[i])[0]
            else:
                alergeno = Alergeno.objects.get_or_create(nombre=i)[0]
            if i=='No tiene':
                if alergeno in alergenos:
                    alergenos.remove(alergeno)
                continue
            alergenos.add(alergeno)
        producto.alergenos.set(list(alergenos))
        producto.save()
        
        ing = producto.ingredientes
        non_vegans_ing_list = open("Scrappers/non-vegan-ingredients-list.txt").read().splitlines()
        for non_vegan in non_vegans_ing_list:
            if non_vegan.lower() in ing.lower(): 
                producto.vegano = False
                break
        producto.save()

        iteration += 1
