from django import forms
from .models import Inventario


class InventarioForm(forms.ModelForm):

    class Meta:
        model = Inventario

        fields = [
            "codigo",
            "nombre",
            "categoria",
            "carrera",
            "sede",
            "cantidad",
            "estado",
            "observacion",
        ]

        widgets = {
            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "categoria": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "carrera": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "sede": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1
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

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]

        if cantidad < 1:
            raise forms.ValidationError(
                "La cantidad debe ser mayor que cero."
            )

        return cantidad