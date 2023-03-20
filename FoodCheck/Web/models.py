from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class Alergeno(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    imagen = models.URLField(validators=[URLValidator()], blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class Supermercado(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    foto = models.URLField(validators=[URLValidator()])

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nombre = models.TextField(max_length=100)
    imagen = models.URLField(validators=[URLValidator()])
    #precio = models.FloatField()
    ingredientes = models.CharField(max_length=2500)
    marca = models.CharField(max_length=50)
    vegano = models.BooleanField(default=True)
    supermercados = models.ManyToManyField(Supermercado)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    valoracionMedia = models.FloatField(default=0)

    def __str__(self):
        return self.nombre + ' - ' + self.marca
    
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    telefono = models.CharField(max_length=50)
    recetaDiaria = models.BooleanField(null=True)
    premiumHasta = models.DateField(null=True)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    es_vegano = models.BooleanField(default=False)

class ListaCompra(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return "Lista de la compra de" , self.usuario.id
    
class Receta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)
    tiempoPreparacion = models.IntegerField()
    publica = models.BooleanField()
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre + ' - ' + self.propietario.nombre

class Valoracion(models.Model):
    id = models.AutoField(primary_key=True)
    puntuacion = models.IntegerField()
    comentario = models.CharField(max_length=200, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.nombre + ' - ' + self.producto.nombre + ' - ' + str(self.puntuacion)
    
class RecetasDesbloqueadasUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    disponible = models.BooleanField()
    fechaBloqueo = models.DateField()

    def __str__(self):
        return self.usuario.nombre + ' - ' + self.receta.nombre + ' - ' + str(self.disponible)
    
class ReporteAlergenos(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    alergenos = models.ManyToManyField(Alergeno)
    fecha = models.DateTimeField(default=datetime.now())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario","producto"],
                name="unique_usuario_producto"
            )
        ]
    
    def __str__(self):
        return "Reporte: user(" + str(self.usuario.id) + ") - producto (" + str(self.producto.id) + ")"