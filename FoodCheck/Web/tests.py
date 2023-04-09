from django.test import TestCase, Client
from django.db import connection
from Web.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Test_premium(StaticLiveServerTestCase):
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
        usuario= User.objects.create(username="pruebapremium",
                password="pbkdf2_sha256$390000$KcrvVW94qU7dxTzlXFF22i$shL3hhA9biQBrGPIgOvLOd7hhd/4mYN1oF7FmwZUb2Q=",
                first_name="test-premium",
                last_name="kikonacho",
                email="test@gmail.com",
                telefono=123456789,
                is_active = True,
                )
        usuario.save()

  def test_become_premium(self):
        url='%s%s' % (self.live_server_url, '/login/')
        self.selenium.get(url)
        self.selenium.set_window_size(1936, 1096)
        username_input = self.selenium.find_element(By.NAME, "username_or_email")
        username_input.send_keys('pruebapremium')
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
        usuario = User.objects.get(username='pruebapremium')
        self.assertIsNotNone(usuario.subscription)