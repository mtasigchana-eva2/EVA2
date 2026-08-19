from django import forms
from .models import SolicitudEquipo


class SolicitudEquipoForm(forms.ModelForm):

    class Meta:
        model = SolicitudEquipo
        fields = [
            "estudiante",
            "carrera",
            "profesor",
            "equipo",
            "cantidad",
            "numero_equipo",
            "numero_serie",
            "fecha_inicio",
            "fecha_fin",
            "motivo",
            "documento",
        ]

        widgets = {
            "estudiante": forms.TextInput(attrs={"class": "form-control"}),
            "carrera": forms.TextInput(attrs={"class": "form-control"}),
            "profesor": forms.TextInput(attrs={"class": "form-control"}),
            "equipo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "numero_equipo": forms.TextInput(attrs={"class": "form-control"}),
            "numero_serie": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }