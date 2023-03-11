from urllib.request import urlopen
import json
import time
import random
import re

from Web.models import Producto, Supermercado


TIEMPO_EXCESO_DE_PETICIONES = 300
TIEMPO_MIN_POR_PETICION = 3
TIEMPO_MAX_POR_PETICION = 5

API_URL = 'https://tienda.mercadona.es/api/'
ENDPOINT_CATEGORIAS = API_URL + 'categories/'
ENDPOINT_PRODUCTOS = API_URL + 'products/'

def hacer_peticion(url):
    time.sleep(random.random() * (TIEMPO_MAX_POR_PETICION - TIEMPO_MIN_POR_PETICION) + TIEMPO_MIN_POR_PETICION)
    try:
        respuesta = urlopen(url).read()
        return json.loads(respuesta)
    except Exception as e:
        if 'Too Many Requests' in str(e):
            print(f'Pausando Scrapping durante {TIEMPO_EXCESO_DE_PETICIONES/60} minutos por exceso de peticiones')
            time.sleep(TIEMPO_EXCESO_DE_PETICIONES)
            return hacer_peticion(url)
        if 'HTTP Error 410: Gone' != str(e):
            print('Error en la petición ' + url)
            print(e)
        return None

def obtener_categorias():
    categorias_finales = []
    datos = hacer_peticion(ENDPOINT_CATEGORIAS)
    categorias = datos['results']

    for categoria in categorias:
        categorias_finales.append({'id': categoria['id'], 'nombre': categoria['name'], 'orden': categoria['order'], 'publicado': categoria['published']})
        for sub_categoria in categoria['categories']: 
            categorias_finales.append({'id': sub_categoria['id'], 'nombre': sub_categoria['name'], 'orden': sub_categoria['order'], 'publicado': sub_categoria['published']})
    return categorias_finales

def obtener_productos_de_categoria(id_categoria):
    productos_finales = []
    categorias = []
    for _ in range(3):
        datos = hacer_peticion(ENDPOINT_CATEGORIAS + str(id_categoria))
        try:
            categorias = datos['categories']
            break
        except:
            print('Error con la categoria %s' % id_categoria)
    for categoria in categorias:
        productos = categoria['products']
        for producto in productos:
            productos_finales.append(producto['id'])
    return productos_finales

def obtener_datos_de_producto(id_producto):
    producto = hacer_peticion(ENDPOINT_PRODUCTOS + str(id_producto))
    if producto is None:
        return producto
    return {
        'id': producto['id'],
        'ean': producto['ean'],
        'nombre': producto['display_name'],
        'imagen': producto['photos'][0]['regular'],
        'marca': producto['brand'] or 'Desconocida',
        'ingredientes': producto['nutrition_information']['ingredients'],
        'alergenos': producto['nutrition_information']['allergens'],
    }

def actualizar_datos_mercadona():

    try:
        mercadona = Supermercado.objects.get(id=1)
    except Supermercado.DoesNotExist:
        mercadona = Supermercado.objects.create(id=1, nombre='Mercadona', foto='https://1000marcas.net/wp-content/uploads/2021/09/Mercadona-Logo.png')
    
    categorias = obtener_categorias()
    productos_comprobados = set()

    for categoria in categorias:
        cantidad_actual = 0
        productos = obtener_productos_de_categoria(categoria['id'])
        for id_producto in productos:
            if id_producto in productos_comprobados:
                continue
            p = obtener_datos_de_producto(id_producto)
            if p is None:
                continue
            productos_comprobados.add(p['id'])
            if p['ingredientes'] is None or p['ingredientes'] == "":
                continue
            
            ingredientes = re.sub(r'<\/?\w+>', '', p['ingredientes'])
            # alergenos = re.sub(r'<\/?\w+>', '', p['alergenos'])

            try:
                producto = Producto.objects.get(id=int(p['ean']))
                producto.nombre = p['nombre']
                producto.imagen = p['imagen']
                producto.ingredientes = ingredientes
                producto.marca = p['marca']
                if mercadona not in producto.supermercados.all():
                    producto.supermercados.add(mercadona)
                producto.save()
                
            except Producto.DoesNotExist:
                producto = Producto.objects.create(
                    id=int(p['ean']),
                    nombre=p['nombre'],
                    imagen=p['imagen'],
                    ingredientes=ingredientes,
                    marca=p['marca'])
                producto.supermercados.set([mercadona])
                producto.save()
            
            ing = producto.ingredientes
            non_vegans_ing_list = open("Scrappers/non-vegan-ingredients-list.txt").read().splitlines()
            for non_vegan in non_vegans_ing_list:
                if non_vegan.lower() in ing.lower(): 
                    producto.vegano = False
                    break
            producto.save()
            

            cantidad_actual += 1
            if cantidad_actual >= 5:
                break

        print('Productos de la categoria %s guardados' % categoria['nombre'])
