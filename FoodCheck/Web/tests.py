import time
from django.test import Client, TestCase

from django.test import TestCase
from django.db import connection
from Web.models import User, Producto, ListaCompra, Receta, Supermercado, Valoracion, Alergeno
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
import unittest


class TrendingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    @classmethod
    def tearDownClass(self) -> None:
        Producto.objects.all().delete()
        Supermercado.objects.all().delete()
        Alergeno.objects.all().delete()
        Valoracion.objects.all().delete()
        User.objects.all().delete()
        return super().tearDownClass()

    def setUp(self):
        self.client = Client()
        users = []
        for i in range(5):
            #Habría que borrar los users
            users.append(User.objects.create_user(username='trend1ng_tust'+str(i), password='123', telefono='12345678'+str(i)))
        self.user = users[0]
        productos_a_valorar = []
        productos_a_valorar.extend(Producto.objects.order_by('?')[:5])
        # Las valoraciones que voy a aplicar en cada producto
        valoraciones = [
            [1, 3, 4, 1, 3], # Para el primer producto (indice 0) 12
            [5, 5], # Para el segundo producto 10
            [4, 5, 5, 5],# Para el tercer producto 19
            [1, 4, 5, 2],# Para el cuarto producto 12
            [3, 2, 1]# Para el quinto producto 6
        ]
       
        
        for indice_producto,valoraciones_producto in enumerate(valoraciones):
            product = productos_a_valorar[indice_producto]
            for indice_usuario,valoracion in enumerate(valoraciones_producto):
                user = users[indice_usuario]
                Valoracion.objects.create(puntuacion = valoracion, usuario = user, producto = product)
            product.valoracionMedia = sum(valoraciones_producto)/len(valoraciones_producto)
            product.save()
            
                
                
        self.valoraciones = valoraciones
        productos_ordenados = sorted(productos_a_valorar, key=lambda p: p.get_popularity(), reverse=True)
        self.productos = productos_ordenados
        time.sleep(3)
        self.login()

    def tearDown(self) -> None:
        return super().tearDown()
        
    def login(self):
        self.client.force_login(self.user)
        
    def test_trending_is_showing(self):
        self.login()
        response = self.client.get('/trending/')
        self.assertIs(response.status_code, 200)
        products_trending = response.context["products"]
        time.sleep(3)
        productos = []
        for indice_p,v in enumerate(self.valoraciones):
            productos.append((self.productos[indice_p],self.productos[indice_p].get_popularity()))
        self.assertEqual(productos,products_trending,"Los objetos trending no son los esperados.")
