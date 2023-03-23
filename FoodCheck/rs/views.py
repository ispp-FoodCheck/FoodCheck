from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from FoodCheck.Web.models import User
from django.http import HttpResponse

@login_required(login_url='authentication:login')
def recommendations(request):
    user = User.objects.get(username = request.user)
    if user is None:
        return HttpResponse("Usuario no logeado")
    else:
        return HttpResponse(str(user))

    
