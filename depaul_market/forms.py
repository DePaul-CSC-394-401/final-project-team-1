from django import forms
from django.forms import ModelForm
from .models import Products
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from .models import Products, Profile  # Add Profile here


# Existing ProductsForm
class ProductsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Give Item a Name'}))

    class Meta:
        model = Products
        fields = ['image', 'name', 'price', 'description']



# New form for updating email
class EmailUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Update your email'}))

    class Meta:
        model = User
        fields = ['email']

# New form for editing the introduction in the Profile
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # Use the Profile model
        fields = ['introduction']  # Only include the introduction field
        widgets = {
            'introduction': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'})
        }


class EditListingForm(forms.ModelForm):
    class Meta:
        model = Products  # Use Products instead of Listing
        fields = ['image', 'name', 'price', 'description']
