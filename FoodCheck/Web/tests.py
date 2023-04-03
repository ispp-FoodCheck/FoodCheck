from django.test import TestCase, Client
from django.db import connection
from Web.models import User, Producto, ListaCompra, Receta, Supermercado
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

class ShoppingListTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shoppinglist_testing', password='123', telefono='123456789')
        self.receta = Receta.objects.create(nombre='Receta de prueba', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas')
        self.receta.productos.set(Producto.objects.order_by('?')[4:7])
        self.receta.save()
    
    def login(self):
        self.client.force_login(self.user)
    
    def test_add_and_remove_product(self):
        self.login()
        product = Producto.objects.order_by('?')[0]
        
        # Adding a product
        self.client.get('/product/%s/add' % product.id)
        response = self.client.get('/shopping_list/')
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        # Check if the html view contains the product
        self.assertContains(response, product.nombre)
        
        # Check if the context contains the product data
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        # Market
        products_per_market = response.context['productos_agrupados_por_supermercado']
        self.assertGreater(len(set(products_per_market.keys()).intersection(set(product.supermercados.all()))), 0, 'The view context doesn\'t have the target market.')
        # Product
        self.assertTrue(product in products_per_market[product.supermercados.all()[0]], 'The view context doesn\'t contains the product')
        self.assertTrue(ListaCompra.objects.get(usuario=self.user).productos.contains(product), 'The ShoppingList model should contain the target product.')
        
        # Removing a product
        self.client.get('/product/%s/remove' % product.id)
        response = self.client.get('/shopping_list/')
        
        # Check if the html view doesn't contain the product
        self.assertNotContains(response, product.nombre)
        
        # Check if the context doesn't contain the product data
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        products_per_market = response.context['productos_agrupados_por_supermercado']
        all_products = sum([sum(products) for products in products_per_market])
        self.assertIs(all_products, 0, 'The shopping list must be empty and it wasn\'t.')
        
        self.assertIs(ListaCompra.objects.get(usuario=self.user).productos.count(), 0, 'The ShoppingList model should be empty.')
    
    def test_add_ingredients(self):
        self.login()
        response = self.client.post('/recipe/%s/details' % self.receta.id, {'añadir-productos': ''})
        self.assertRedirects(response, '/shopping_list/')
        
        response = self.client.get('/shopping_list/')
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        for product in self.receta.productos.all():
            # Check if the html view contains the product
            self.assertContains(response, product.nombre)
            
            # Check if the context contains the product data
            self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
            # Market
            products_per_market = response.context['productos_agrupados_por_supermercado']
            self.assertGreater(len(set(products_per_market.keys()).intersection(set(product.supermercados.all()))), 0, 'The view context doesn\'t have the target market.')
            # Product
            self.assertTrue(product in products_per_market[product.supermercados.all()[0]], 'The view context doesn\'t contains the product.')
            self.assertTrue(ListaCompra.objects.get(usuario=self.user).productos.contains(product), 'The ShoppingList model should contain the target product.')
        
    
    def test_availability(self):
        response = self.client.get('/shopping_list/')
        self.assertRedirects(response, '/login/?next=/shopping_list/')
        self.login()
        response = self.client.get('/shopping_list/')
        
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        
        products_per_market = response.context['productos_agrupados_por_supermercado']
        all_products = sum([sum(products) for products in products_per_market])
        self.assertIs(all_products, 0, 'The shopping list must be empty and it wasn\'t')
        
        self.assertIs(ListaCompra.objects.get(usuario=self.user).productos.count(), 0, 'The ShoppingList model should be empty.')



class ListaDeLaCompraSeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        usuario= User.objects.create(username="Chema01111",
                password="pbkdf2_sha256$390000$t6AOcTYO68UNOzN7egezgY$bIoyek57DKTOQinE/ZrfrDQA6t971fFt2+Z6raILUac=",
                first_name="Albaricoque",
                last_name="Franco",
                email="cocas@gmail.com",
                telefono=23456789,
                is_active = True,
                )
        usuario.save()

        supermercado= Supermercado.objects.create(nombre="Carrefour",
                             foto="https://1000marcas.net/wp-content/uploads/2020/11/Carrefour-Logo.png"
                             )
        supermercado.save()

        producto= Producto.objects.create(id=1,
                                nombre="Garbanzos",
                                imagen="https://prod-mercadona.imgix.net/images/8a6cce24488444736497d91a7a5ec404.jpg?fit=crop&h=600&w=600",
                                ingredientes="",
                                marca="Hacendado"
                                )
        producto.supermercados.set([supermercado])
        producto.save()
        
        listacompra= ListaCompra.objects.create(usuario=usuario) 
        listacompra.productos.set([producto])       
        listacompra.save()
        
    def test_login(self):
        url='%s%s' % (self.live_server_url, '/login/')
        self.selenium.get(url)
        username_input = self.selenium.find_element(By.NAME, "username_or_email")
        username_input.send_keys('Chema01111')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('root')
        butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
        ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
        self.selenium.implicitly_wait(30)
        butom_input.click()
        producto_gamba = self.selenium.find_element(By.XPATH, "/html/body/header/nav/div/div/ul/li[2]/a")
        producto_gamba.click()
        producto_lista_garbanzos= self.selenium.find_element(By.XPATH,"/html/body/main/div[2]/div/div/div/div/p[1]")
        Garbanzos=producto_lista_garbanzos.text
        self.assertEqual(Garbanzos,"Garbanzos")
        self.selenium.quit()