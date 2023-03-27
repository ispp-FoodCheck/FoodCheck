from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.http import require_safe
from rs.rs import get_all_valorations_correct_format, get_recommendations
from payments.utils import es_premium
from Web.models import Producto

@login_required(login_url='authentication:login')
@require_safe
def recommendations(request):
    user = request.user
    if not es_premium(user):
        return redirect("/checkout")

    #ratings = get_all_valorations_correct_format()
    #recs = [recs_rating[1] for recs_rating in get_recommendations(ratings,user)]
    recs = []
    return render(request, "recommendations.html", {'products':recs})