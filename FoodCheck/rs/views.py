from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from rs.rs import get_all_valorations_correct_format, getRecommendations
from payments.utils import es_premium
from rs.generador import generar_puntuaciones

@login_required(login_url='authentication:login')
def recommendations(request):
    user = request.user
    
    ratings = get_all_valorations_correct_format()
    recs = [recs_rating[1] for recs_rating in getRecommendations(ratings,user)]
    return render(request, "recommendations.html", {'products':recs})




            



    

    
