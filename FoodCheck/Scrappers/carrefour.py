import re
from urllib.request import urlopen
import json

from Web.models import Producto, Supermercado

num_elementos='5'

url_keywords = "https://www.carrefour.es/search-api/suggestions/v1/empathize?lang=es&catalog=food&rows="+ num_elementos


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
    url_search = "https://www.carrefour.es/search-api/query/v1/search?lang=es&query="+ keyword + "&rows=" + str(num_elementos)
    # Realizamos la solicitud HTTP a la página de Carrefour
    response = urlopen(url_search)

    # Leemos el contenido de la respuesta HTTP
    content = response.read()

    # Cerramos la conexión
    response.close()

    # Analizamos el contenido JSON de la respuesta
    data = json.loads(content)

    # Imprimimos todos los nombres de producto encontrados
    #impressions = json.loads(data["analytics"]["impressions"])
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
        marca = '-'    
    try:
        marca = product['brand']['description']
    except KeyError:
        marca = '-'
    try:
        alergenos = product['nutrition_info']['alergenos']['contiene']
    except KeyError:
        alergenos = '-'
    try:
        ingredientes = re.sub(r'<\/?\w+>', '', product['nutrition_info']['ingredientes'])[:2000]
    except KeyError:
        ingredientes = '-'    

    
    return {
        'id': product_id,
        'ean': ean,
        'nombre': nombre,
        'imagen': imagen,
        'marca': marca,
        'ingredientes': ingredientes,
        'alergenos': alergenos,
        'vegano':True
    }

def main():
    try:
        carrefour = Supermercado.objects.get(id=2)
    except Supermercado.DoesNotExist:
        carrefour = Supermercado.objects.create(id=2, nombre='Carrefour', foto='https://1000marcas.net/wp-content/uploads/2020/11/Carrefour-Logo.png')
        

    keywords = find_keywords()

    products_ids = []

    for keyword in keywords:
         products_ids.extend(search_products(keyword))
    
    for product_id in products_ids:
        detailed_product = product_details(product_id)
        if not isinstance(detailed_product, int):
            try:
                producto = Producto.objects.get(id=int(detailed_product['ean']))
                producto.nombre = detailed_product['nombre']
                producto.imagen = detailed_product['imagen']
                producto.ingredientes = detailed_product['ingredientes']
                producto.marca = detailed_product['marca']
                producto.vegano = detailed_product['vegano']
                if carrefour not in producto.supermercados.all():
                    producto.supermercados.add(carrefour)
                producto.save()
                
            except Producto.DoesNotExist:
                producto = Producto.objects.create(
                    id=int(detailed_product['ean']),
                    nombre=detailed_product['nombre'],
                    imagen=detailed_product['imagen'],
                    ingredientes= detailed_product['ingredientes'],
                    vegano = detailed_product['vegano'],
                    marca=detailed_product['marca'])
                producto.supermercados.set([carrefour])
                producto.save()

if __name__ == '__main__':
    main()