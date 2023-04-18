from django.db import connection
from django.test import Client, TestCase, tag
from Web.models import User, Valoracion, Producto
import datetime
from random import randint
from rs.rs import get_all_valorations_correct_format, get_recommendations

@tag("fast")
class RecommendationTestCase(TestCase):

    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())
    
    def setUp(self):
        self.client = Client()
        self.userNoPremium = User.objects.create_user(username='recommendation_no_premium_user', password='123', telefono='123456789')
        self.userPremium = User.objects.create_user(username='recommendation_premium_user', password='123', telefono='123456789', premiumHasta=datetime.date.today() + datetime.timedelta(days=1))
        self.crear_valoraciones_aleatorias()

    def tearDown(self):
        self.userNoPremium.delete()
        self.userPremium.delete()
    
    def login(self, premium = True):
        if premium:
            self.client.force_login(self.userPremium)
        else:
            self.client.force_login(self.userNoPremium)

    def test_no_premium_user_cannot_access(self):
        self.login(premium=False)
        response = self.client.get("/recommendations/")
        self.assertNotEqual(response.status_code, 200, 'Usuario no premium puede acceder a recomendaciones')

    def test_recommendations(self):
        self.login()
        response = self.client.get("/recommendations/")
        self.assertEqual(response.status_code, 200, 'Usuario premium no puede acceder a las recomendaciones')
        productos_recomendados = response.context["products"]
        recs = [recs_rating[1] for recs_rating in get_recommendations(get_all_valorations_correct_format(),self.userPremium)]

        self.assertEquals(productos_recomendados, recs, "Los productos mostrados en la vista no son los que el sistema recomienda")


    def crear_valoracion(self, usuario, producto, puntuacion, comentario):

        valoracion = Valoracion.objects.create(comentario=comentario, puntuacion=puntuacion, usuario=usuario, producto=producto)
        valoracion.save()
        valoraciones = Valoracion.objects.filter(producto=producto).all()
        puntuaciones = [v.puntuacion for v in valoraciones]
        media = sum(puntuaciones) / len(puntuaciones)
        producto.valoracionMedia = media
        producto.save()

    def crear_valoraciones_aleatorias(self):
        for user_index in range(0,5):
            user_valorador = User.objects.create_user(username='user_valorador_' + str(user_index), password='123', telefono='123456789')
            for producto_index in range(0,20):
                if randint(0,19) < 14:      #Valorar 3 de cada 4 productos aprox
                   puntuacion = randint(1,5)
                   producto = Producto.objects.all()[producto_index]
                   self.crear_valoracion(user_valorador, producto, puntuacion, "Comentario")
        for producto_index in range(0,20):
                if randint(0,19) < 14:      
                   puntuacion = randint(1,5)
                   producto = Producto.objects.all()[producto_index]
                   self.crear_valoracion(self.userPremium, producto, puntuacion, "Comentario")
