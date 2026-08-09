from django import forms
from .models import Herramienta


class HerramientaForm(forms.ModelForm):

    class Meta:
        model = Herramienta
        fields = "__all__"

        widgets = {

            "inventario": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "numero_serie": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "marca": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "estado": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "observacion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

        }