from django import forms
from django.forms import ModelForm
from .models import Products
from django.contrib.auth.models import User

class ProductsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Give Item a Name'}))

    class Meta:
        model = Products
        fields = ['image', 'name', 'price', 'description']
        
