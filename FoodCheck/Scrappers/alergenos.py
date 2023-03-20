from Web.models import Alergeno


LACTEOS = 'lacteos'
PESCADO = 'pescado'
CACAHUETES = 'cacahuetes'
CRUSTACEOS = 'crustaceos'
HUEVOS = 'huevos'
APIO = 'apio'
MOSTAZA = 'mostaza'
SESAMO = 'sesamo'
SULFITOS = 'sulfitos'
ALTRAMUZ = 'altramuz'
MOLUSCOS = 'moluscos'
SOJA = 'soja'
GLUTEN = 'gluten'
FRUTOS_SECOS = 'frutos secos'

PALABRAS_CLAVE_INTOLERANCIAS = {
    LACTEOS: [
        'lacteo', 'leche', 'lactosa', 'queso',
    ],
    PESCADO: [],
    CRUSTACEOS: [
        'crustaceo'
    ],
    CACAHUETES: [],
    FRUTOS_SECOS: [],
    APIO: [],
    MOSTAZA: [],
    SESAMO: [],
    SULFITOS: [],
    ALTRAMUZ: [
        'altramuces'
    ],
    MOLUSCOS: [
        'molusco',
    ],
    HUEVOS: [
        'huevo', 'clara de huevo',
    ],
    SOJA: [],
    GLUTEN: []
}

MAPA_INTOLERANCIAS_MERCADONA = {
    'cereales que contengan gluten': GLUTEN,
    'trigo y productos derivados': GLUTEN,
    'centeno y productos derivados': GLUTEN,
    'crustáceos y productos a base de crustáceos': CRUSTACEOS,
    'huevos y productos a base de huevo': HUEVOS,
    'cacahuetes y productos a base de cacahuetes': CACAHUETES,
    'pescado y productos a base de pescado': PESCADO,
    'soja y productos a base de soja': SOJA,
    'leche y sus derivados (incluida la lactosa)': LACTEOS,
    'frutos de cáscara': FRUTOS_SECOS,
    'apio y productos derivados': APIO,
    'mostaza y productos derivados': MOSTAZA,
    'granos de sésamo y productos a base de granos de sésamo': SESAMO,
    'dióxido de azufre y sulfitos': SULFITOS,
    'altramuces y productos a base de altramuces': ALTRAMUZ,
    'moluscos y productos a base de moluscos': MOLUSCOS,
}

MAPA_INTOLERANCIAS_CARREFOUR = {
    'Cereales que contienen gluten': GLUTEN,
    'Crustáceos': CRUSTACEOS,
    'Huevo': HUEVOS,
    'cacahuetes': CACAHUETES,
    'pescado': PESCADO,
    'Soja': SOJA,
    'Leche': LACTEOS,
    'Frutos de cáscara': FRUTOS_SECOS,
    'Apio': APIO,
    'Mostaza': MOSTAZA,
    'Semillas de sésamo': SESAMO,
    'Sulfitos': SULFITOS,
    'Altramuces o lupino': ALTRAMUZ,
    'Moluscos': MOLUSCOS,
}



def obtener_alergenos_de_texto(texto):
    alergenos = []
    for alergeno in PALABRAS_CLAVE_INTOLERANCIAS.keys():
        intolerancia = Alergeno.objects.get_or_create(nombre=alergeno)[0]
        if alergeno in texto.lower():
            alergenos.append(intolerancia)
            continue
        for palabra in PALABRAS_CLAVE_INTOLERANCIAS[alergeno]:
            if palabra in texto.lower():
                alergenos.append(intolerancia)
                break
    return alergenos