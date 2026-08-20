from django import forms

from .models import SolicitudEquipo
from inventario.models import Inventario


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

            "estudiante": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "carrera": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "profesor": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "equipo": forms.Select(
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

            "numero_equipo": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "numero_serie": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "motivo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

            "documento": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Mostramos el stock disponible en cada opción.
        equipos = Inventario.objects.select_related(
            "sede"
        ).order_by(
            "nombre",
            "sede__nombre"
        )

        opciones = []

        for equipo in equipos:

            disponible = equipo.cantidad_disponible

            texto = (
                f"{equipo.nombre} "
                f"- {equipo.sede.nombre} "
                f"({disponible} disponibles)"
            )

            opciones.append(
                (
                    equipo.id,
                    texto
                )
            )

        self.fields["equipo"].choices = [
            ("", "Seleccione un equipo")
        ] + opciones

        # Si estamos editando una solicitud ya existente,
        # guardamos la referencia.
        self.solicitud_actual = self.instance

    def clean_cantidad(self):

        cantidad = self.cleaned_data.get(
            "cantidad"
        )

        if not cantidad or cantidad < 1:

            raise forms.ValidationError(
                "La cantidad debe ser mayor que cero."
            )

        equipo = self.cleaned_data.get(
            "equipo"
        )

        if not equipo:
            return cantidad

        disponible = equipo.cantidad_disponible

        # Si estamos editando una solicitud que ya estaba
        # aprobada, sus propias unidades están actualmente
        # descontadas del stock.
        #
        # Por eso las devolvemos temporalmente al cálculo.
        if (
            self.instance
            and self.instance.pk
            and self.instance.inventario_descontado
            and self.instance.equipo_id == equipo.id
        ):

            disponible += self.instance.cantidad

        if cantidad > disponible:

            raise forms.ValidationError(
                f"Solo existen {disponible} unidades "
                f"disponibles de este equipo en esta sede."
            )

        return cantidad