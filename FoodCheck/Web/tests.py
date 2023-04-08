from django.test import TestCase, Client
from django.db import connection
from Web.models import User, Producto, ListaCompra, Receta, Supermercado
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
import os

class RecipeSearchTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    def setUp(self):
        self.URL_RECIPES = '/recipes'
        self.client = Client()
        fecha_premium = date.today() + timedelta(days=1)
        self.user = User.objects.create_user(username='user1', password='123', telefono='123456789', premiumHasta=fecha_premium)

        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')
        
            self.receta1 = Receta.objects.create(nombre='Receta1', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas', imagen=imagen)
            self.receta1.productos.set(Producto.objects.all()[4:7])
            self.receta1.save()

            self.receta2 = Receta.objects.create(nombre='Receta2', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas', imagen=imagen)
            self.receta2.productos.set(Producto.objects.all()[10:13])
            self.receta2.save()

            imagen.close()

        f.close()

    def tearDown(self):
        self.receta1.delete()
        self.receta2.delete()

    def login(self):
        self.client.force_login(self.user)

    def test_search_all_recipes(self):
        self.login()
        response = self.client.post(self.URL_RECIPES, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

        response = self.client.get(self.URL_RECIPES)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

    def test_search_recipe(self):
        self.login()
        response = self.client.post(self.URL_RECIPES, {'busqueda':'Receta1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')
       
        response = self.client.post(self.URL_RECIPES, {'busqueda':'1111111'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')

    def test_search_recipe_by_product(self):
        self.login()

        producto1 = Producto.objects.all()[11]
        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

        producto2 = Producto.objects.all()[5]
        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')

        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto1.id, producto2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')