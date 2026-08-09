from django import forms
from .models import Permiso


class PermisoForm(forms.ModelForm):

    class Meta:
        model = Permiso
        # Se elimina 'estado' de la lista para que el estudiante no pueda cambiarlo
        fields = [
            "estudiante",
            "carrera",
            "docente",
            "fecha_inicio",
            "fecha_fin",
            "motivo",
            "documento",
        ]

        widgets = {
            "estudiante": forms.TextInput(attrs={"class": "form-control"}),
            "carrera": forms.TextInput(attrs={"class": "form-control"}),
            "docente": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }