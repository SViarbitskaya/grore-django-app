from django import forms
from django.conf import settings
from django.utils.translation import gettext

class ImageSearchForm(forms.Form):
    search_query = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': gettext("Search"),
            'class': 'form-control me-2' 
        }),
        max_length=100,
        required=False,
        label=False
        )