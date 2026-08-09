from django import forms
from .models import Sede


class SedeForm(forms.ModelForm):

    class Meta:

        model = Sede

        fields = "__all__"

        widgets = {

            "nombre": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "ciudad": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "direccion": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "telefono": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "estado": forms.CheckboxInput(attrs={
                "class":"form-check-input"
            }),

        }