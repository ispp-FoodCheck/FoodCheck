from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django_resized import ResizedImageField

from Web.models import User, Alergeno, ListaCompra, Producto, Receta

class RegistroForm(UserCreationForm):
    email = forms.EmailField()
    telefono = forms.CharField(max_length=20)
    alergenos = forms.ModelMultipleChoiceField(
        queryset=Alergeno.objects.filter(imagen__isnull=False),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    es_vegano = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'telefono', 'alergenos','es_vegano')
    
    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.telefono = self.cleaned_data['telefono']
        user.es_vegano=self.cleaned_data['es_vegano']
        if commit:
            user.save()
            user_lista = ListaCompra.objects.create(usuario=user)
            user_lista.save()
        for alergeno in self.cleaned_data['alergenos']:
            user.alergenos.add(alergeno)
        return user

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Nombre de User o correo electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class AllergenReportForm(forms.Form):
    allergens = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Alergeno.objects.filter(imagen__isnull=False),
        label="Seleccione los alérgenos:"
    )