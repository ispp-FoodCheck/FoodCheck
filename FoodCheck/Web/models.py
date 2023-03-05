from django.db import models
from django.core.validators import URLValidator

class Alergeno(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class Supermercado(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    foto = models.URLField(validators=[URLValidator()])

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    imagen = models.URLField(validators=[URLValidator()])
    #precio = models.FloatField()
    ingredientes = models.CharField(max_length=2000)
    marca = models.CharField(max_length=50)
    supermercados = models.ManyToManyField(Supermercado)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    vegano = models.BooleanField(blank=True)

    def __str__(self):
        return self.nombre + ' - ' + self.marca
    
class Usuario(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    usuario = models.CharField(max_length=50)
    contraseña = models.CharField(max_length=50)
    recetaDiaria = models.BooleanField()
    premiumHasta = models.DateField()   
    alergenos = models.ManyToManyField(Alergeno, blank=True)

    def __str__(self):
        return self.nombre + ' - ' + self.usuario

class ListaCompra(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return "Lista de la compra: "+self.nombre + ' - ' + self.usuario.nombre
    
class Receta(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)
    tiempoPreparacion = models.IntegerField()
    publica = models.BooleanField()
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre + ' - ' + self.propietario.nombre
    

class Valoracion(models.Model):
    id = models.IntegerField(primary_key=True)
    puntuacion = models.IntegerField()
    comentario = models.CharField(max_length=200)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.nombre + ' - ' + self.producto.nombre + ' - ' + str(self.puntuacion)
    
class RecetasDesbloqueadasUsuario(models.Model):
    id = models.IntegerField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    disponible = models.BooleanField()
    fechaBloqueo = models.DateField()

    def __str__(self):
        return self.usuario.nombre + ' - ' + self.receta.nombre + ' - ' + str(self.disponible)