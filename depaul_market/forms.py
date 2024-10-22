from django import forms
from django.forms import ModelForm
from .models import Products, Wallet
from django.contrib.auth.models import User

class ProductsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Give Item a Name'}))

    class Meta:
        model = Products
        fields = ['image', 'name', 'price', 'description']
<<<<<<< Updated upstream
        
=======



# New form for updating email
class EmailUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Update your email'}))

    class Meta:
        model = User
        fields = ['email']


class EditListingForm(forms.ModelForm):
    class Meta:
        model = Products  # Use Products instead of Listing
        fields = ['image', 'name', 'price', 'description']

class Walletform(forms.ModelForm):
    money = forms.DecimalField(max_digits=100, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Enter Amount'}))
    class Meta:
        model = Wallet
        fields = []
>>>>>>> Stashed changes
