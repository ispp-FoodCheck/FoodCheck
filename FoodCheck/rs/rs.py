# A dictionary of movie critics and their ratings of a small
# set of movies

from math import sqrt

from generador import generar_puntuaciones



# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]: 
        if item in prefs[p2]: si[item] = 1 #??

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0 #Si no teneis items en común, similaridad = 0
  
    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si]) #Si Migue a platano le ha dao un 3, a mandarina un 4 y a platnao un 5 pues = 3+4+5 = 12
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si]) #Si Migue a platano le ha dao un 3, a mandarina un 4 y a platnao un 5 pues = 9+16+25 = 50
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])	

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r

# Returns the best matches for person from the prefs dictionary. #Devuelve las n personas que más se parecen a person.
# Number of results and similarity function are optional params.
def topMatches(prefs,person,n=5,similarity=sim_pearson):
  scores=[(similarity(prefs,person,other),other) 
                  for other in prefs if other!=person]
  scores.sort()
  scores.reverse()
  return scores[0:n]


#FUNCION PRINCIPAL: Hace recomendaciones de items a un usuario usando un RS Colaborativo basado en Usuarios.
#RS basado en memoria. 
def getRecommendations(prefs,person,similarity=sim_pearson):
  totals={}
  simSums={}
  for other in prefs:
    if other==person: continue # don't compare me to myself
    sim=similarity(prefs,person,other)
    print("Similaridad de ", person, " con ", other, ": ", sim)
    
    if sim<=0: continue# ignore scores of zero or lower
    for item in prefs[other]:
	    
      # only score what I haven't seen yet
      if item not in prefs[person] or prefs[person][item]==0:
        # Similarity * Score. #Totals es un diccionario que contiene: clave: item. Valor: suma acumulativa de la puntuación de un usuario * coeficiente del user con la persona objetivo.
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # Sum of similarities #SimSums es un diccionario que contiene: clave: item. Valor: suma acumulativa del coeficiente de sim entre usuario y usuario objetivo.
        simSums.setdefault(item,0)
        simSums[item]+=sim

  # Create the normalized list
  '''
  rankings = []
  for item, total in totals.items():
    res1 = total/simSums[item]
    res2 = item
    rankings.append( (res1, res2) )
  '''
  #Rankings es una lista de tuplas que contiene (Puntuacion pa recomendar el item, item).
  rankings=[(total/simSums[item],item) for item,total in totals.items()]

  #Pone primero la puntuación porque por defecto se ordena en base la primer elemento de la tupla.
  #Se ordena de menor a mayor y por eso se hace el reverse.
  rankings.sort()
  rankings.reverse()
  return rankings


def returnDiccMatchesAlready(lista, dicc):
  res= {}
  for puntuacion, usuario in lista:
    res[usuario] = dicc[usuario]
  return res

#####Puntuaciones contiene un diccionario tal que: {Usuarios, {Productos, Valoracion del usuario}}
puntuaciones = generar_puntuaciones()
print("PUNTUACIONES")
print(list(puntuaciones.items()))
print("\n---------------------------------\n")
#resultado = topMatches(puntuaciones, list(puntuaciones)[0])
#print(resultado)
#print("\n---------------------------------\n")
#dicc_reducido = returnDiccMatchesAlready(resultado,puntuaciones)
#sim_pearson(puntuaciones,'migue','chema')
#print(dicc_reducido)
#print("\n---------------------------------\n")
print(getRecommendations(puntuaciones,'Migue'))
print("\n---------------------------------\n")
#Traza de test:
#Primero: Ver qué usuarios se pareecen más a un usuario dado (Migue)
#Segundo: Tenemos los usuarios que se parecen más a Migue.
#Tercero: Ahora tenemos que encontrar los productos que esos Usuarios   #Qué pasa si los usuarios si los
'''
()
('Clara', {'Pizza barbacoa': 1, 'Platano': 4, 'Mandarina': 1, 'Bollicao': 1, 'Nocilla': 4, 'Carne pollo': 0, 'Arroz': 4, 'Chocoflakes': 3})

(2-1) (1-0) (5-4) 
'''

migueclara = {'Migue': {'Lechuga': 5, 'Mandarina': 2, 'Melon': 3, 'Pan de centeno': 5, 'Carne pollo': 1, 'Pera': 3, 'Platano': 5, 'Kiwi': 5},'Clara': {'Pizza barbacoa': 1, 'Platano': 4, 'Mandarina': 1, 'Bollicao': 1, 'Nocilla': 4, 'Carne pollo': 0, 'Arroz': 4, 'Chocoflakes': 3}}
print("Puntuacion: ",sim_pearson(migueclara, 'Migue', 'Clara'))