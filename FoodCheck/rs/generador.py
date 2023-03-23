import random

# 'Migue' : {'Carne ternera' : 0.0, 'Carne pollo' : 1.0, 'Leche' : 2.0, 'Leche de avellanas' : 5.0, 'Pizza barbacoa' : 4.0, 'Manzana' : 5.0, 'Mandarina' : 5.0,'Brocoli' : 2.0, 'Tosta Rica' : 5.0, 'Platano': 5.0, 'Arroz' : 3.5, 'Lechuga' : 2.5}
comidas = ['Carne ternera', 'Carne pollo', 'Leche', 'Leche de avellanas', 'Pizza barbacoa', 'Manzana', 'Mandarina','Brocoli', 'Tosta Rica', 'Platano', 'Arroz', 'Lechuga','Pera','Sandia','Melon','Kiwi','Granada','Nocilla','Bollicao','Chocoflakes','Nutella','Pan de centeno','Ensalada caprichosa']
nombres = ['Migue','Juan','Kiko','Pablo','Marta','Nacho','Maria','Julia','Josemi','Clara','David','Dolores','Povedano','Gomez','Dani','Ricardo','Nuria']

def generar_puntuaciones():
    # random.seed(4)
    puntuaciones = {}

    for nombre in nombres:
        puntuaciones[nombre] = {comida:random.randint(0, 5) for comida in random.choices(comidas, k=9)}

    return puntuaciones