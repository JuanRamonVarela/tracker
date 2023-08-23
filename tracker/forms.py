from django import forms
from .models import Categories, Books

class CategoriesForm(forms.ModelForm):
    model=Categories
    fields=['category',]