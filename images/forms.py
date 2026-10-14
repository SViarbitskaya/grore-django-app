from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy

class ImageSearchForm(forms.Form):
    search_query = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': gettext_lazy("What are you looking for?"),
            'class': 'form-control me-2' 
        }),
        max_length=100,
        required=False,
        label=False
        )