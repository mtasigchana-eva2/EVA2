from django import forms
from .models import Solicitud


class SolicitudForm(forms.ModelForm):

    class Meta:
        model = Solicitud
        fields = [
            "carrera",
            "sede",
            "docente",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "motivo",
            "documento",
        ]

        widgets = {
            "carrera": forms.Select(attrs={"class": "form-select"}),
            "sede": forms.Select(attrs={"class": "form-select"}),
            "docente": forms.TextInput(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "documento": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }