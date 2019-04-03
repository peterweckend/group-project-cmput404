from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.forms import ModelForm

class CustomUserCreationForm(UserCreationForm):

    github_id = forms.CharField(required=False)


    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'displayname', 'email', 'github_id')
        labels = {
            'displayname': 'Display name',
            'github_id': 'Github Username'
        }
        widgets = {
            'password': forms.PasswordInput(),
        }
    def save(self, user=None):
        user_profile = super(CustomUserCreationForm, self).save(commit=False)
        if user:
            user_profile = user 
        user_profile.is_active= False
        user_profile.save()
        return user_profile

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
        widgets = {
            'password': forms.PasswordInput(attrs={'class':'password'}),
            
        }

