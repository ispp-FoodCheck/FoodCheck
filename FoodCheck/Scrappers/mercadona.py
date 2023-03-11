from urllib.request import urlopen
import json
import time
import random
import re

from Web.models import Producto, Supermercado, Alergeno


TIEMPO_EXCESO_DE_PETICIONES = 300
TIEMPO_MIN_POR_PETICION = 3
TIEMPO_MAX_POR_PETICION = 5

API_URL = 'https://tienda.mercadona.es/api/'
ENDPOINT_CATEGORIAS = API_URL + 'categories/'
ENDPOINT_PRODUCTOS = API_URL + 'products/'

KEYWORDS_INTOLERANCIAS = {
    'cereales que contengan gluten': 'gluten',
    'trigo y productos derivados': 'gluten',
    'centeno y productos derivados': 'gluten',
    'crustáceos y productos a base de crustáceos': 'crustaceos',
    'huevos y productos a base de huevo': 'huevos',
    'cacahuetes y productos a base de cacahuetes': 'cacahuetes',
    'pescado y productos a base de pescado': 'pescado',
    'soja y productos a base de soja': 'soja',
    'leche y sus derivados (incluida la lactosa)': 'lacteos',
    'frutos de cáscara': 'frutos secos',
    'apio y productos derivados': 'apio',
    'mostaza y productos derivados': 'mostaza',
    'granos de sésamo y productos a base de granos de sésamo': 'sesamo',
    'dióxido de azufre y sulfitos': 'sulfitos',
    'altramuces y productos a base de altramuces': 'altramuz',
    'moluscos y productos a base de moluscos': 'moluscos',
}

def hacer_peticion(url):
    time.sleep(random.random() * (TIEMPO_MAX_POR_PETICION - TIEMPO_MIN_POR_PETICION) + TIEMPO_MIN_POR_PETICION)
    try:
        conexion = urlopen(url)
        datos = json.loads(conexion.read())
        conexion.close()
        return datos
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
        'alergenos': producto['nutrition_information']['allergens'] or '',
    }

def actualizar_datos_mercadona():

    mercadona = Supermercado.objects.get_or_create(nombre='Mercadona', defaults={'foto':'https://1000marcas.net/wp-content/uploads/2021/09/Mercadona-Logo.png'})[0]
    
    categorias = obtener_categorias()
    productos_comprobados = set()
    random.shuffle(categorias)

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
            alergenos = map(lambda x: x.lower(), p['alergenos'].split('.'))
            lista_alergenos = []
            for posible_alergeno in alergenos:
                intolerancia = None
                if 'libre' in posible_alergeno:
                    continue
                alergeno = re.search(r'<strong>(.*?)<\/strong>', posible_alergeno)
                if alergeno is None:
                    continue
                alergeno = alergeno.group(1)
                if alergeno in KEYWORDS_INTOLERANCIAS.keys():
                    intolerancia = Alergeno.objects.get_or_create(nombre=KEYWORDS_INTOLERANCIAS[alergeno])[0]
                else:
                    intolerancia = Alergeno.objects.get_or_create(nombre=alergeno)[0]
                lista_alergenos.append(intolerancia)
            
            producto, created = Producto.objects.get_or_create(id=int(p['ean']), defaults={
                'nombre': p['nombre'],
                'imagen': p['imagen'],
                'ingredientes': ingredientes,
                'marca': p['marca']
            })
            if created:
                producto.supermercados.set([mercadona])
            else:
                producto.nombre = p['nombre']
                producto.imagen = p['imagen']
                producto.ingredientes = ingredientes
                producto.marca = p['marca']
                if mercadona not in producto.supermercados.all():
                    producto.supermercados.add(mercadona)
            producto.alergenos.set(lista_alergenos)
            producto.save()
            
            # TODO: Logica para saber alergenos

            cantidad_actual += 1
            if cantidad_actual >= 5:
                break

        print('Productos de la categoria %s guardados' % categoria['nombre'])
