from django import forms
from .models import SolicitudHerramienta


class SolicitudHerramientaForm(forms.ModelForm):

    class Meta:
        model = SolicitudHerramienta
        # Se elimina 'estado' de la lista
        fields = [
            "estudiante",
            "carrera",
            "profesor",
            "herramienta",
            "cantidad",
            "fecha_inicio",
            "fecha_fin",
            "motivo",
            "documento",
        ]

        widgets = {
            "estudiante": forms.TextInput(attrs={"class": "form-control"}),
            "carrera": forms.TextInput(attrs={"class": "form-control"}),
            "profesor": forms.TextInput(attrs={"class": "form-control"}),
            "herramienta": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }