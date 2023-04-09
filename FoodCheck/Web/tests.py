from datetime import date, timedelta
import time
from django.test import TestCase, Client
from django.db import connection
from Web.models import Producto, User, Receta, ListaCompra, Supermercado
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

class RecipesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='recipe_test', password='123', telefono='123456789')

    def login(self):
        self.client.force_login(self.user)

    def test_add_recipe(self):
        self.login()
        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')        
        
        productos=[2996514000002,3560071092801]
        response = self.client.post('/recipes/new',{'nombre':'Receta','cuerpo':'Prueba de receta','horas':'1','minutos':'0',
                                                    'segundos':'0','checkbox_publica':'si','receta_imagen':imagen,'productos':productos}, follow=True)
        receta = Receta.objects.filter(nombre='Receta',descripcion='Prueba de receta')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(receta[0].nombre, 'Receta')
        self.assertEqual(receta[0].descripcion, 'Prueba de receta')

class RecipeNegativeSeleniumTest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        usuario= User.objects.create(username="recipe_test",
                password="pbkdf2_sha256$390000$t6AOcTYO68UNOzN7egezgY$bIoyek57DKTOQinE/ZrfrDQA6t971fFt2+Z6raILUac=",
                first_name="recipe_test",
                last_name="Recetas",
                email="recipe@gmail.com",
                telefono=23456789,
                is_active = True,
                )
        usuario.save()

    def test_ahorasi(self):
        url='%s%s' % (self.live_server_url, '/login/')
        self.driver.get(url)
        self.driver.find_element(By.ID, "username_or_email").click()
        self.driver.find_element(By.ID, "username_or_email").send_keys("recipe_test")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("root")
        self.driver.find_element(By.ID, "logBtn").click()
        self.driver.find_element(By.ID, "navbarDropdown").click()
        self.driver.find_element(By.LINK_TEXT, "Mis recetas").click()
        self.driver.find_element(By.LINK_TEXT, "Nueva receta").click()
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "nombre").click()
        self.driver.find_element(By.ID, "nombre").send_keys("hola")
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "cuerpo").click()
        self.driver.find_element(By.ID, "cuerpo").send_keys("hola")
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "buscadorProductosReceta").click()
        element = self.driver.find_element(By.ID, "buscadorProductosReceta")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "buscadorProductosReceta").send_keys("pe")
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "horas").click()
        self.driver.find_element(By.ID, "horas").send_keys("hola")
        time.sleep(3)
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        self.driver.find_element(By.ID, "minutos").click()
        self.driver.find_element(By.ID, "minutos").send_keys("hola")
        time.sleep(3)
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')
        
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