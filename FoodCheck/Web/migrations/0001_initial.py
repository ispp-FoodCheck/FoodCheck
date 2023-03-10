# Generated by Django 4.1.7 on 2023-03-12 15:39

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alergeno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('imagen', models.URLField(blank=True, null=True, validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('imagen', models.URLField(validators=[django.core.validators.URLValidator()])),
                ('ingredientes', models.CharField(max_length=2500)),
                ('marca', models.CharField(max_length=50)),
                ('vegano', models.BooleanField(default=True)),
                ('valoracionMedia', models.FloatField(default=0)),
                ('alergenos', models.ManyToManyField(blank=True, to='Web.alergeno')),
            ],
        ),
        migrations.CreateModel(
            name='Receta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=200)),
                ('tiempoPreparacion', models.IntegerField()),
                ('publica', models.BooleanField()),
                ('productos', models.ManyToManyField(to='Web.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Supermercado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('foto', models.URLField(validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('apellidos', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=50)),
                ('usuario', models.CharField(max_length=50)),
                ('contrase??a', models.CharField(max_length=50)),
                ('recetaDiaria', models.BooleanField()),
                ('premiumHasta', models.DateField(null=True)),
                ('alergenos', models.ManyToManyField(blank=True, to='Web.alergeno')),
            ],
        ),
        migrations.CreateModel(
            name='Valoracion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('puntuacion', models.IntegerField()),
                ('comentario', models.CharField(max_length=200, null=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.usuario')),
            ],
        ),
        migrations.CreateModel(
            name='RecetasDesbloqueadasUsuario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('disponible', models.BooleanField()),
                ('fechaBloqueo', models.DateField()),
                ('receta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.receta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='receta',
            name='propietario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.usuario'),
        ),
        migrations.AddField(
            model_name='producto',
            name='supermercados',
            field=models.ManyToManyField(to='Web.supermercado'),
        ),
        migrations.CreateModel(
            name='ListaCompra',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('productos', models.ManyToManyField(to='Web.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.usuario')),
            ],
        ),
    ]
