from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.http import require_safe

import Web.forms as forms
from .decorators import user_not_authenticated

@require_safe
@user_not_authenticated
def registro(request):
    if request.method == 'POST':
        form = forms.RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = forms.RegistroForm()
    return render(request, 'register.html', {'form': form})

@require_safe
@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@require_safe
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
                messages.success(request, f"Bienvenido, {user.username}!")
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = forms.LoginForm()

    return render(request, 'login.html', {'form': form})
