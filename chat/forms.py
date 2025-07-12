from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """
    Custom user registration form
    """
    email = forms.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and ' ' in username:
            raise forms.ValidationError('Username cannot contain spaces.')
        return username

class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile
    """
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'phone', 'location', 'website', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        } 