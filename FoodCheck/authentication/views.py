import Web.forms as forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_safe
from Web.models import Alergeno

from .decorators import user_not_authenticated


@user_not_authenticated
def registro(request):
    alergenos = Alergeno.objects.all()
    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Te has registrado correctamente!')
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = forms.RegistroForm()
    return render(request, 'register.html', {'form': form, 'alergenos':alergenos})

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@user_not_authenticated
def login_view(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Bienvenido!")
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form})


@user_not_authenticated
def terms_view(request):
    return render(request, 'terms.html')
