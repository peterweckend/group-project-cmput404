from django import forms
from users.models import CustomUser
from .models import Comment,Post
# This must support markdown
# Maybe have a button that tells the post to display it in markdown
# When the user selects 2/shared author, another HTML form should become unhidden
# I assume we would use JavaScript for this, possibly vue
privacyOptions = [
    ("1", "Just Me"), 
    ("2","One other person"), 
    ("3", "Friends"), 
    ("4", "Friends of Friends"),
    ("5", "Only Friends on Connectify"),
    ("6","Public"),
    ("7","Unlisted")]

    # unlisted posts should generate a random post ID (check its not taken first)
    # large scale could be done better, for now can do it more simply

class uploadForm(forms.Form):
    # Furthermore, a post should require at least a summary or an image
    title = forms.CharField(label='Title', max_length=24, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Post Title...'
        }))
    body = forms.CharField(label='Body', max_length=250, required = False, widget=forms.Textarea(
        attrs={
            'rows':7,
            'class': 'form-control',
            'placeholder': 'Write a post...'
        }))
    markdown = forms.BooleanField(required = False)
    imageLink = forms.ImageField(label="Image",required = False)
    privacy = forms.CharField(label='Privacy', widget=forms.Select(choices=privacyOptions))
    # If we wanted to get fancy, this could autofill from the user's friends
    sharedAuthor = forms.CharField(label='Shared Author', required = False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Shared Author?...'
        }))

class friendRequestForm(forms.Form):
    # Basically will just be a char field
    # Actually, this should just be a button that appears on a users profile
    # So to be even more honest we might not even need a form for this, but its
    # not a big deal right now
    friendToAdd = forms.CharField(label="Author's Username", max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter a userame...'
        }))

class acceptIgnoreRequestForm(forms.Form):
    # This will simply be a button with an invisible value
    # nvm this might be a stupid idea
    pass

class EditProfileForm(forms.ModelForm):
    displayname = forms.CharField(label='New Display Name', max_length=24, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter Display Name...'
        }))
    class Meta:
        model = CustomUser
        fields = ['displayname']
        
    def save(self, user=None):
        user_profile = super(EditProfileForm, self).save(commit=False)
        if user:
            user_profile = user 
        user_profile.save()
        return user_profile
        
class commentForm(forms.ModelForm):
    body = forms.CharField(label='New Comment', widget=forms.Textarea(
        attrs={
            'rows':3,
            'class': 'form-control',
            'placeholder': 'Enter comment...'
        }))
    class Meta:
        model=Comment
        fields= ['body']
