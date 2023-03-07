from django.shortcuts import render
from .models import Producto, Alergeno

# Create your views here.

def index(request):
    alergenos_selected = request.GET.getlist('alergenos')

    alergenos = Alergeno.objects.all()

    lista_producto = Producto.objects.exclude(alergenos__nombre__in=alergenos_selected)

    if request.GET.get('vegano'):
        lista_producto = lista_producto.filter(vegano=True)
        vegano_selected = True
    else:
        vegano_selected = False

    diccionario={'lista_producto':lista_producto,'alergenos_available':alergenos,'alergenos_selected':alergenos_selected,'vegano_selected':vegano_selected}
    return render(request,"products.html",diccionario)