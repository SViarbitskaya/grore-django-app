from django import forms
from django.conf import settings

class ImageSearchForm(forms.Form):
    search_query = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': "What's on your mind?"}),
        max_length=100,
        required=False,
        label=False
        )