from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.forms import ModelForm

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'displayname', 'email')
        widgets = {
            'password': forms.PasswordInput(),
        }

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
        widgets = {
            'password': forms.PasswordInput(attrs={'class':'password'}),
            
        }

class EditProfileForm(ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ['displayname']