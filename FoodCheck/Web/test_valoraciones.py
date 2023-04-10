from django.db import connection
from django.test import Client, TestCase
from Web.models import Producto, User


class RatingsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rating_test', password='123', telefono='123456789')

    def login(self):
        self.client.force_login(self.user)

    def test_add_review(self):
        self.login()
        product = Producto.objects.order_by('?')[0]
        response = self.client.post('/product/%s/details' % product.id, {"cuerpo": "Me gusta este producto", "valoracion": 5})
        self.assertIs(response.status_code, 200, 'Logged user cannot add review')
        self.assertContains(response, "Me gusta este producto")
        self.assertContains(response, "5,00")

    def test_add_review_negative(self):
        self.login()
        product = Producto.objects.order_by('?')[0]
        response = self.client.post('/product/%s/details' % product.id, {"cuerpo": "Me gusta este producto", "valoracion": 5})
        self.assertIs(response.status_code, 200, 'Logged user cannot add review')
        response = self.client.post('/product/%s/details' % product.id, {"cuerpo": "No aparezco", "valoracion": 2})
        self.assertNotContains(response,"No aparezco")
        self.assertNotContains(response, "2,00")

    def test_change_average_review(self):
        self.login()
        product = Producto.objects.order_by('?')[0]
        initial_response = self.client.get('/product/%s/details' % product.id)
        self.assertContains(initial_response, "0,00")
        self.assertNotContains(initial_response, "5,00")
        response = self.client.post('/product/%s/details' % product.id, {"cuerpo": "Me gusta este producto", "valoracion": 5})
        self.assertContains(response, "5,00")
        self.assertNotContains(response, "0,00")


