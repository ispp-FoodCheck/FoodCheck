import datetime
import os
import requests
import time

from django.test import TestCase, Client
from django.db import connection
from Web.models import User, Receta, Producto
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from django.core.files.uploadedfile import SimpleUploadedFile


class Test_premium(StaticLiveServerTestCase):
     
      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

      @classmethod
      def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

      def setUp(self):
        usuario= User.objects.create(username="usuarioNOpremium",
                password="pbkdf2_sha256$390000$KcrvVW94qU7dxTzlXFF22i$shL3hhA9biQBrGPIgOvLOd7hhd/4mYN1oF7FmwZUb2Q=",
                first_name="test-premium",
                last_name="kikonacho",
                email="test@gmail.com",
                telefono=123456789,
                is_active = True,
                )
        usuario.save()

        # usuario2 premium para comprobar funcionalidades
        usuario2 = User.objects.create(username="usuarioYApremium",
                password="pbkdf2_sha256$390000$KcrvVW94qU7dxTzlXFF22i$shL3hhA9biQBrGPIgOvLOd7hhd/4mYN1oF7FmwZUb2Q=",
                first_name="test-premium",
                last_name="test",
                email="test2@gmail.com",
                telefono=123456789,
                is_active = True,
                premiumHasta = datetime.date(2024,1,1)
                )
        usuario2.save()
        
        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')

        receta = Receta.objects.create(nombre='Receta para desbloqueo y añadido de productos',
                                      descripcion='Probando',
                                      propietario=usuario,
                                      publica=True,
                                      imagen=imagen,
                                      tiempoPreparacion='2 horas')
        receta.productos.set(Producto.objects.order_by('?')[4:7])
        receta.save()

        receta = Receta.objects.create(nombre='Receta para desbloqueo > 1',
                                      descripcion='Probando',
                                      propietario=usuario,
                                      publica=True,
                                      imagen=imagen,
                                      tiempoPreparacion='2 horas')
        receta.productos.set(Producto.objects.order_by('?')[4:7])
        receta.save()

      def tearDown(self):
        Receta.objects.all().delete()
        User.objects.all().delete()
        

      def test_become_premium(self):
            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioNOpremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()
            self.selenium.find_element(By.LINK_TEXT, "Plan premium").click()
            self.selenium.find_element(By.LINK_TEXT, "Hacerse premium!").click()
            self.selenium.find_element(By.ID, "email").click()
            self.selenium.find_element(By.ID, "email").send_keys("test@gmail.com")
            self.selenium.find_element(By.ID, "cardNumber").click()
            self.selenium.find_element(By.ID, "cardNumber").send_keys("4242 4242 4242 4242")
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "cardCvc").click()
            self.selenium.find_element(By.ID, "cardCvc").send_keys("424")
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "cardExpiry").send_keys("01 / 42")
            self.selenium.find_element(By.ID, "billingName").click()
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "billingName").click()
            self.selenium.find_element(By.ID, "billingName").send_keys("Prueba")
            self.selenium.find_element(By.CSS_SELECTOR, ".SubmitButton-IconContainer").click()
            wait = WebDriverWait(self.selenium,10)
            wait.until(EC.url_contains('/payment_completed'))
            session_id = self.selenium.current_url.split("=")[1]
            url='%s%s' % (self.live_server_url, '/payment_completed?session_id=' + str(session_id))
            self.selenium.get(url)

            usuario = User.objects.get(username='usuarioNOpremium')
            self.assertIsNotNone(usuario.subscription)

      def test_recetaPrivadaPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            #Creando una receta privada 

            # ruta necesaria para añadir imagen a receta
            rutaRelativa = "Web\\static\\imgs\\lechuga.png"
            rutaAbsoluta = os.path.abspath(rutaRelativa)
            print(rutaAbsoluta)

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Mis recetas").click()
            self.selenium.find_element(By.LINK_TEXT, "Nueva receta").click()
            self.selenium.find_element(By.ID, "nombre").click()
            self.selenium.find_element(By.ID, "nombre").send_keys("test")
            self.selenium.find_element(By.ID, "cuerpo").click()
            self.selenium.find_element(By.ID, "cuerpo").send_keys("test")
            self.selenium.find_element(By.ID, "buscadorProductosReceta").click()
            self.selenium.find_element(By.ID, "buscadorProductosReceta").send_keys("Queso")
            time.sleep(0.5)
            self.selenium.find_element(By.LINK_TEXT, "Queso semicurado mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.LINK_TEXT, "Queso tierno mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.ID, "receta_imagen").send_keys(rutaAbsoluta)
            self.selenium.find_element(By.ID, "horas").click()
            self.selenium.find_element(By.ID, "horas").send_keys("05")
            self.selenium.find_element(By.ID, "minutos").click()
            self.selenium.find_element(By.ID, "minutos").send_keys("05")
            self.selenium.find_element(By.ID, "segundos").click()
            self.selenium.find_element(By.ID, "segundos").send_keys("05")
            self.selenium.find_element(By.ID, "checkbox_publica").click()
            self.selenium.find_element(By.ID, "filter-form").click()
            self.selenium.find_element(By.ID, "boton-busqueda").click()

            #Comprobamos la redirección a my_recipes

            url_esperada = "http://localhost:8000/my_recipes/"
            self.assertTrue(self.selenium.current_url, url_esperada)

      def test_accesoDiscoverPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            # Accede al sistema de recomendación

            self.selenium.find_element(By.LINK_TEXT, "Discover").click()
            titulo_visible = self.selenium.find_element(By.CLASS_NAME, "title")
            self.assertIsNotNone(titulo_visible)

      def test_desbloquearReceta_anadirProductos(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div/div/a/img').click() #receta 1

            compruebaRecetaBloqueada = self.selenium.find_element(By.ID, "boton-desbloqueo")
            self.assertIsNotNone(compruebaRecetaBloqueada)

            # Desbloqueamos
            self.selenium.find_element(By.ID, "boton-desbloqueo").click()

            compruebaRecetaDesbloqueada = self.selenium.find_element(By.ID, "boton-productos-lista")
            self.assertIsNotNone(compruebaRecetaDesbloqueada)

            # Añadimos sus productos a la lista de compra
            self.selenium.find_element(By.ID, "boton-productos-lista").click()

            redireccionOK = self.selenium.find_element(By.XPATH, "/html/body/main/div[2]/div/h1")
            self.assertIsNotNone(redireccionOK)

            # comprobamos que el user premium puede desbloquear más de una receta:

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div[2]/div/a/img').click() # receta 2
            self.selenium.find_element(By.ID, "boton-desbloqueo").click()
            compruebaRecetaDesbloqueada2 = self.selenium.find_element(By.ID, "boton-productos-lista")
            self.assertIsNotNone(compruebaRecetaDesbloqueada2)


            
          


            
            
              

