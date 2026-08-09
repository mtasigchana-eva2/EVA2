from django import forms
from usuarios.models import Perfil


class PerfilForm(forms.ModelForm):

    class Meta:

        model = Perfil

        fields = [
            "rol",
            "carrera",
            "sede",
            "descripcion",
            "estado",
        ]

        widgets = {

            "rol": forms.Select(
                attrs={"class": "form-select"}
            ),

            "carrera": forms.Select(
                attrs={"class": "form-select"}
            ),

            "sede": forms.Select(
                attrs={"class": "form-select"}
            ),

            "descripcion": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "estado": forms.Select(
                attrs={"class": "form-select"}
            ),
        }