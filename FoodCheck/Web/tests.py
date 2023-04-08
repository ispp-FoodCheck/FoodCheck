from django.test import TestCase, Client
from django.db import connection
from Web.models import User


####TESTS LISTADO PRODUCTO####

class ShoppingListTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='products_testing', password='123', telefono='123456789')

    def login(self):
        self.client.force_login(self.user)

    def test_pagination(self):
        self.login()

        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)

        # Comprobamos que en la primera página hay 12 productos
        self.assertTrue(len(response.context['lista_producto']) == 12, "El número de elementos en la página no es correcto")

        # Navegamos a la página 2, y a la última página, y comprobamos que existan
        response = self.client.post('/home', {'page': '2'})
        self.assertEqual(response.status_code, 200, "Se ha intentado navegar a una página que no existe")
        self.assertEquals(response.context['lista_producto'].number, 2, "La página a la que se ha navegado no es la página 2")

        num_paginas = response.context['total_de_paginas']
        response = self.client.post('/home', {'page': num_paginas})
        self.assertEqual(response.status_code, 200, "Se ha intentado navegar a una página que no existe")
        self.assertEquals(response.context['lista_producto'].number, num_paginas, "La página a la que se ha navegado no es la última página")

        # Intentamos navegar a una página que no exista, esto debería llevarnos a la última página

        response = self.client.post('/home', {'page': num_paginas + 20})
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['lista_producto'].number, num_paginas, "La página a la que se ha navegado no es la última página")

        response = self.client.post('/home', {'page': -1})
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['lista_producto'].number, num_paginas, "La página a la que se ha navegado no es la última página")

    def test_buscador(self):
        self.login()

        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)

        # Realizamos una búsqueda de un objeto que existe en la BD, 'Gambón' debería devolver 2 resultados
        response = self.client.post('/home', {'canal_de_texto': 'Gambón'})
        self.assertTrue(len(response.context['lista_producto']) == 2, "El número de elementos en la página no es correcto")

        # Ahora realizamos una búsqueda de un objeto que no exista en la BD
        response = self.client.post('/home', {'canal_de_texto': 'nóbmaG'})
        self.assertFalse(len(response.context['lista_producto']) != 0, "El número de elementos en la página no es correcto")


    def test_filtros(self):
        self.login()

        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        num_paginas_sin_filtrar = response.context['total_de_paginas']

        response2 = self.client.post('/home', {'alergenos_selected': ('lacteos')})
        num_paginas_filtradas = response2.context['total_de_paginas']

        self.assertNotEqual(num_paginas_sin_filtrar, num_paginas_filtradas)

