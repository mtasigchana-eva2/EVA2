from django import forms
from .models import Biometria


class BiometriaForm(forms.ModelForm):

    class Meta:

        model = Biometria

        fields = [
            "foto"
        ]