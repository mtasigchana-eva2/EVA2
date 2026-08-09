from django import forms
from .models import Inventario

class InventarioForm(forms.ModelForm):

    class Meta:
        model = Inventario
        fields = "__all__"

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "categoria": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "carrera": forms.Select(attrs={
                "class": "form-select"
            }),

            "sede": forms.Select(attrs={
                "class": "form-select"
            }),

            "cantidad": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "estado": forms.Select(attrs={
                "class": "form-select"
            }),

            "observacion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
        }