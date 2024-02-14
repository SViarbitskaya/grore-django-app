from django import forms

class ImageSearchForm(forms.Form):
    search_query = forms.CharField(label='Search', max_length=100, required=False)