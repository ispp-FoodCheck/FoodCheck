from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django_resized import ResizedImageField
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django import forms
from django.db.models import Avg

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
    ingredientes = models.CharField(max_length=2500)
    marca = models.CharField(max_length=50)
    vegano = models.BooleanField(default=True)
    supermercados = models.ManyToManyField(Supermercado)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    valoracionMedia = models.FloatField(default=0)

    def __str__(self):
        return self.nombre + ' - ' + self.marca

    def __gt__(self, other):
        return self.nombre > other.nombre
    
    def actualizar_valoracion_media(self):
        self.valoracionMedia = Valoracion.objects.filter(producto=self).aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0.0
        self.save()
    
class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    telefono = models.CharField(max_length=50)
    recetaDiaria = models.DateField(null=True)
    premiumHasta = models.DateField(null=True)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    es_vegano = models.BooleanField(default=False)
    subscription = models.CharField(max_length=200, null=True, blank=False)

class ListaCompra(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return "Lista de la compra de " + self.usuario.username
    
class Receta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField(max_length=50, null=False, blank=False)
    descripcion = models.CharField(max_length=4000, null=False, blank=False)
    tiempoPreparacion = models.TextField(max_length=70, null=False, blank=False)
    publica = models.BooleanField(null=False, blank=False)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = ResizedImageField(size=[300, 300], upload_to='recetas', null=True)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre + ' - ' + self.propietario.username

@receiver(pre_delete, sender=Receta)
def receta_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.imagen.delete(False)

class Valoracion(models.Model):
    id = models.AutoField(primary_key=True)
    puntuacion = models.IntegerField()
    comentario = models.CharField(max_length=200, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.username + ' - ' + self.producto.nombre + ' - ' + str(self.puntuacion)
    
class RecetasDesbloqueadasUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    fechaBloqueo = models.DateField()

    def __str__(self):
        return self.usuario.username + ' - ' + self.receta.nombre

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