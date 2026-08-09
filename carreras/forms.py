from django import forms
from .models import Carrera


class CarreraForm(forms.ModelForm):

    class Meta:

        model = Carrera

        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "estado",
        ]

        widgets = {

            "codigo": forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Ejemplo: DSW"
            }),

            "nombre": forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Nombre de la carrera"
            }),

            "descripcion": forms.Textarea(attrs={
                "class":"form-control",
                "rows":4
            }),

            "estado": forms.CheckboxInput(attrs={
                "class":"form-check-input"
            }),

        }