# A dictionary of movie critics and their ratings of a small
# set of movies

from math import sqrt

from generador import generar_puntuaciones


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(user_prod_rating,p1,p2):
  # Get the list of mutually rated items
  si={}
  for item in user_prod_rating[p1]: 
    if item in user_prod_rating[p2]: si[item]=1

  # if there are no ratings in common, return 0
  if len(si)==0: return 0

  # Sum calculations
  n=len(si)
  
  # Sums of all the preferences #Coge la puntuación de cada item que ha puntuao p1 y las suma
  sum1=sum([user_prod_rating[p1][it] for it in si])
  #Coge la puntuación de cada item que ha puntuao p2(que también ha puntuao pq) y las suma
  sum2=sum([user_prod_rating[p2][it] for it in si])
  
  # Sums of the squares
  sum1Sq=sum([pow(user_prod_rating[p1][it],2) for it in si])
  sum2Sq=sum([pow(user_prod_rating[p2][it],2) for it in si])	
  
  # Sum of the products
  pSum=sum([user_prod_rating[p1][it]*user_prod_rating[p2][it] for it in si])
  
  # Calculate r (Pearson score)
  num=pSum-(sum1*sum2/n)
  den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
  if den==0: return 0

  r=num/den

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
    # don't compare me to myself
    if other==person: continue
    sim=similarity(prefs,person,other)

    # ignore scores of zero or lower
    if sim<=0: continue
    for item in prefs[other]:
	    
      # only score movies I haven't seen yet
      if item not in prefs[person] or prefs[person][item]==0:
        # Similarity * Score
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # Sum of similarities
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

  #Pone primero la puntuación porque defecto se ordena en base la primer elemento de la tupla.
  #Se ordena de menor a mayor y por eso se hace el reverse.
  rankings.sort()
  rankings.reverse()
  return rankings




#####Puntuaciones contiene un diccionario tal que: {Usuarios, {Productos, Valoracion del usuario}}
puntuaciones = generar_puntuaciones()
print(list(puntuaciones))
resultado = topMatches(puntuaciones, list(puntuaciones)[0])
print(resultado)
#sim_pearson(puntuaciones,'migue','chema')


#Traza de test:
#Primero: Ver qué usuarios se pareecen más a un usuario dado (Migue)
#Segundo: Tenemos los usuarios que se parecen más a Migue.
#Tercero: Ahora tenemos que encontrar los productos que esos Usuarios   #Qué pasa si los usuarios si los

