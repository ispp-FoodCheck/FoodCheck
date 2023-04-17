from django.test import TestCase, Client, tag
from django.db import connection
from Web.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

@tag("fast")
class LoginRegisterTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    def setUp(self):
        self.client = Client()
        self.credentials = {
            "username": "testuser",
            "password": "12345",
            "password2": "12345",
            "email": "test@gmail.com",
            "first_name": "test",
            "last_name": "user",
            "phone": "123456789"
            }
        self.credentialsNotMatch = {
            "username": "testuser",
            "password": "12345",
            "password2": "123456",
            "email": "test@gmail.com",
            "first_name": "test",
            "last_name": "user",
            "phone": "123456789"
            }
        self.credentialsNotValidEmail = {
            "username": "testuser",
            "password": "12345",
            "password2": "12345",
            "email": "testgmail.com",
            "first_name": "test",
            "last_name": "user",
            "phone": "123456789"
        }
        self.loginCredentials = {
            "username": "testuser",
            "password": "12345"
        }
        self.register_url='/register/'
        self.login_url='/login/'
    
    def test_can_view_register_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_can_view_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_login_success(self):
        User.objects.create_user(username='testuser', password='12345', telefono='123456789')
        response = self.client.post(self.login_url, self.loginCredentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)
    
    def test_cant_login_without_password(self):
        response = self.client.post(self.login_url, {'username': 'testuser'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_cant_login_without_username(self):
        response = self.client.post(self.login_url, {'password': '12345'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_cant_login_with_wrong_password(self):
        User.objects.create_user(username='testuser', password='123456', telefono='123456789')
        response = self.client.post(self.login_url, self.loginCredentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        #self.assertContains(response, 'Usuario o contraseña incorrectos')
    
    def test_logout(self):
        User.objects.create_user(username='testuser', password='12345', telefono='123456789')
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/logout/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

@tag("selenium", "sut")
class LoginRegisterTestSelenium(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.driver = webdriver.Chrome()
    
    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        super().tearDownClass()

    def test_login_register(self):
        #Initial configuration
        url='%s%s' % (self.live_server_url, '/')
        self.driver.get(url)
        self.driver.set_window_size(2000, 2000)
        self.driver.find_element(By.LINK_TEXT, "Empezar ahora").click()

        #Failed register with not matching passwords and not valid email
        self.driver.find_element(By.LINK_TEXT, "Registrarse").click()
        self.driver.find_element(By.ID, "first_name").click()
        self.driver.find_element(By.ID, "first_name").send_keys("Test")
        self.driver.find_element(By.ID, "last_name").send_keys("User")
        self.driver.find_element(By.ID, "telefono").send_keys("123456789")
        self.driver.find_element(By.ID, "email").send_keys("testmail.com")
        self.driver.find_element(By.ID, "username").send_keys("testuser2")
        self.driver.find_element(By.ID, "password1").send_keys("foodchechk1")
        self.driver.find_element(By.ID, "password2").send_keys("foodchechk2")
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "terms").click()
        self.driver.find_element(By.ID, "regBtn").click()

        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".alert:nth-child(1) li").text, "Los dos campos de contraseña no coinciden.")
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".alert:nth-child(2) li").text, "Introduzca una dirección de correo electrónico válida.")

        #Successful register
        self.driver.find_element(By.LINK_TEXT, "Registrarse").click()
        self.driver.find_element(By.ID, "first_name").click()
        self.driver.find_element(By.ID, "first_name").send_keys("Test")
        self.driver.find_element(By.ID, "last_name").send_keys("User")
        self.driver.find_element(By.ID, "telefono").send_keys("123456789")
        self.driver.find_element(By.ID, "email").send_keys("test@gmail.com")
        self.driver.find_element(By.ID, "username").send_keys("testuser")
        self.driver.find_element(By.ID, "password1").send_keys("foodcheck")
        self.driver.find_element(By.ID, "password2").send_keys("foodcheck")
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "nextBtn").click()
        self.driver.find_element(By.ID, "terms").click()
        self.driver.find_element(By.ID, "regBtn").click()
        self.driver.find_element(By.LINK_TEXT, "Iniciar sesión").click()

        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".text").text, "Te has registrado correctamente!")

        #Failed login with not valid password
        self.driver.find_element(By.ID, "username_or_email").click()
        self.driver.find_element(By.ID, "username_or_email").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("foodcheckusertest")
        self.driver.find_element(By.ID, "logBtn").click()

        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".text").text, "Usuario o contraseña incorrectos")

        #Successful login
        self.driver.find_element(By.ID, "username_or_email").click()
        self.driver.find_element(By.ID, "username_or_email").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("foodcheck")
        self.driver.find_element(By.ID, "logBtn").click()

        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".username").text, "testuser")
        self.driver.find_element(By.CSS_SELECTOR, ".username").click()
        
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".dropdown-menu > .dropdown-item:nth-child(1)").text, "Nombre de usuario: testuser")
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(2)").text, "Correo electronico: test@gmail.com")
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(3)").text, "Nombre: Test")
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, ".dropdown-item:nth-child(4)").text, "Apellidos: User")
        self.driver.find_element(By.LINK_TEXT, "Cerrar sesión").click()
        
        self.assertEqual(self.driver.find_element(By.LINK_TEXT, "Iniciar sesión").text, "Iniciar sesión")
        self.assertEqual(self.driver.find_element(By.LINK_TEXT, "Registrarse").text, "Registrarse")
        self.driver.quit()