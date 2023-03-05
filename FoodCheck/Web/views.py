from django.shortcuts import render
from .models import Producto

# Create your views here.

def index(request):
    lista_producto= Producto.objects.all()
    diccionario={'lista_producto':lista_producto}
    return render(request,"products.html",diccionario)