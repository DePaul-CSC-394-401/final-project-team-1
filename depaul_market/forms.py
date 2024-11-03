from django import forms
from django.forms import ModelForm
from .models import CATEGORY_CHOICES, Products, Wallet
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from .models import Products, Profile  # Add Profile here

from .models import Products 

# Existing ProductsForm

class ProductsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Give Item a Name'}))
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="Category", required=True)  # Dropdown for category
    
    # Add availability duration field (optional)
    availability_duration = forms.IntegerField(
        required=False,  # Optional field
        widget=forms.NumberInput(attrs={'placeholder': 'Available for (hours)'}),
        label="Availability Duration (hours)"
    )

    class Meta:
        model = Products  # Specify the model here
        fields = ['image', 'name', 'price', 'description', 'availability_duration','category', 'quality', 'brand', 'color']  # Include all the necessary fields


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
        fields = ['introduction', 'campus']  # Only include the introduction and location field
        widgets = {
            'introduction': forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'})
        }


class EditListingForm(forms.ModelForm):
    class Meta:
        model = Products  # Use Products instead of Listing
        fields = ['image', 'name', 'price', 'description']

class Walletform(forms.ModelForm):
    money = forms.DecimalField(max_digits=100, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Enter Amount'}))
    class Meta:
        model = Wallet
        fields = []