from django import forms
from django.contrib.auth.models import User
from .models import Perfil


class RegistroUsuarioForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        datos = super().clean()

        if datos.get("password") != datos.get("password2"):
            raise forms.ValidationError(
                "Las contraseñas no coinciden."
            )

        return datos


class UserEditarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class PerfilEditarForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            "foto",
            "carrera",
            "sede",
            "telefono",
            "fecha_nacimiento",
            "edad",
            "direccion",
            "descripcion",
        ]
        widgets = {
            "foto": forms.FileInput(attrs={"class": "form-control"}),
            "carrera": forms.Select(attrs={"class": "form-select"}),
            "sede": forms.Select(attrs={"class": "form-select"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "edad": forms.NumberInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }