from math import sqrt
from Web.models import User, Valoracion


def get_all_valorations_correct_format():
    res = {}
    for user in User.objects.all():
        user_rates = {}
        for rate in Valoracion.objects.filter(usuario = user):
            user_rates[rate.producto] = rate.puntuacion
        res[user] = user_rates
    return res

def sim_pearson(prefs, p1, p2):
  products_rated_by_both = []
  for item in prefs[p1]:
    if item in prefs[p2]:
      products_rated_by_both.append(item)
  if len(products_rated_by_both) <= 0:
     return 0
  
  ra = sum(prefs[p1][product] for product in products_rated_by_both)/len(products_rated_by_both)
  rb = sum(prefs[p2][product] for product in products_rated_by_both)/len(products_rated_by_both)
  
  numerator = sum((prefs[p1][product] - ra) * (prefs[p2][product] - rb) for product in products_rated_by_both)
  denominator = sqrt(sum(pow((prefs[p1][product] - ra),2) for product in products_rated_by_both)) * sqrt(sum(pow((prefs[p2][product] - rb),2) for product in products_rated_by_both))
  
  if denominator == 0:
     return 0
  return numerator/denominator
     


#FUNCION PRINCIPAL: Hace recomendaciones de items a un usuario usando un RS Colaborativo basado en Usuarios.
#RS basado en memoria. 
def get_recommendations(prefs,person,similarity=sim_pearson):
  totals={}
  sim_sums={}
  for other in prefs:
    if other==person: continue # don't compare me to myself
    sim=similarity(prefs,person,other)
    
    if sim<=0: continue# ignore scores of zero or lower
    for item in prefs[other]:
	    
      # only score what I haven't seen yet
      if item not in prefs[person] or prefs[person][item]==0:
        # Similarity * Score. #Totals es un diccionario que contiene: clave: item. Valor: suma acumulativa de la puntuación de un usuario * coeficiente del user con la persona objetivo.
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # Sum of similarities #SimSums es un diccionario que contiene: clave: item. Valor: suma acumulativa del coeficiente de sim entre usuario y usuario objetivo.
        sim_sums.setdefault(item,0)
        sim_sums[item]+=sim
  #Rankings es una lista de tuplas que contiene (Puntuacion pa recomendar el item, item).
  rankings=[(total/sim_sums[item],item) for item,total in totals.items()]

  #Pone primero la puntuación porque por defecto se ordena en base la primer elemento de la tupla.
  #Se ordena de menor a mayor y por eso se hace el reverse.
  rankings.sort()
  rankings.reverse()
  return rankings

#####Puntuaciones contiene un diccionario tal que: {Usuarios, {Productos, Valoracion del usuario}}
'''
puntuaciones = generar_puntuaciones()
print("PUNTUACIONES")
print(list(puntuaciones.items()))
print("\n---------------------------------\n")
print(getRecommendations(puntuaciones,'Migue')'''
