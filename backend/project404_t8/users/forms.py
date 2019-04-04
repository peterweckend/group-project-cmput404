from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.forms import ModelForm

class CustomUserCreationForm(UserCreationForm):

    github_url = forms.URLField(required=False)
    displayname = forms.URLField(required=True)
    github_username = forms.CharField(required=False)
    bio = forms.CharField(required=False)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'displayname', 'first_name', 'last_name', 'email', 'github_username', 'github_url', 'bio', 'password1', 'password2')
        labels = {
            'displayname': 'Display Name',
            'github_url': 'Github URL',
            'github_username': 'Github Username',
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

