import os
from locust import HttpUser, TaskSet, between
from django.core.files.uploadedfile import SimpleUploadedFile

from locust import HttpUser, task, between

import string
import random

def random_user_generator(self):
    characters = string.ascii_letters + string.digits
    username=  ''.join(random.choice(characters) for i in range(15))
    password=  ''.join(random.choice(characters) for i in range(15))
    return (username,password)

class QuickstartUser(HttpUser):
    wait_time = between(1, 2)


    def on_start(self):

        response = self.client.get("/register/")
        csrftoken = response.cookies['csrftoken']
        credenciales = random_user_generator(self)
        self.client.post("/register/", {"username":credenciales[0], "password1":credenciales[1],"password2":credenciales[1], "email:": str(credenciales[0]) + "@example.com","telefono": str(987654321),"checkbox": 1}, headers={"X-CSRFToken": csrftoken})


        response = self.client.get("/login/")
        csrftoken = response.cookies['csrftoken']
        self.client.post("/login/", {"username_or_email":credenciales[0], "password":credenciales[1]}, headers={"X-CSRFToken": csrftoken})
        

    def on_finish(self):
        self.client.post("/logout/")

    @task
    def home(self):
        self.client.get("/home")

    @task
    def index(self):
        self.client.get("/")

    @task
    def premium(self):
        self.client.get("/premium")

    @task
    def shopping_list(self):
        self.client.get("/shopping_list")

    @task
    def trending(self):
        self.client.get("/trending")

    @task
    def report(self):
        self.client.get("/report/list")

    @task
    def rate(self):
        response = self.client.get("/product/8480000038241/details")
        csrftoken = response.cookies['csrftoken']
        self.client.post("/product/8480000038241/details", {"valoracion":"3", "cuerpo":"Comentario de test"}, headers={"X-CSRFToken": csrftoken})

    @task
    def recipe(self):
        response = self.client.get("/recipes/new")
        csrftoken = response.cookies['csrftoken']
        with open(os.path.abspath("static\\imgs\\lechuga.png"),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')
            productos=[2996514000002,3560071092801]
            self.client.post('/recipes/new',{'nombre':'Receta'}, headers={"X-CSRFToken": csrftoken})
            f.close()


