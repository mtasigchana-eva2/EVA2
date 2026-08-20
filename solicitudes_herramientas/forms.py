from django import forms

from .models import SolicitudHerramienta


class SolicitudHerramientaForm(forms.ModelForm):

    class Meta:

        model = SolicitudHerramienta

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
            "estudiante": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "carrera": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "profesor": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "herramienta": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "motivo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "documento": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get(
            "fecha_inicio"
        )

        fecha_fin = cleaned_data.get(
            "fecha_fin"
        )

        cantidad = cleaned_data.get(
            "cantidad"
        )

        if (
            fecha_inicio
            and fecha_fin
            and fecha_fin < fecha_inicio
        ):
            self.add_error(
                "fecha_fin",
                "La fecha de finalización no puede ser anterior a la fecha de inicio.",
            )

        if cantidad is not None and cantidad < 1:
            self.add_error(
                "cantidad",
                "La cantidad debe ser mayor que cero.",
            )

        return cleaned_data