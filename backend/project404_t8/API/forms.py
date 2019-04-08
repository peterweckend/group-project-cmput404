from django import forms
from users.models import CustomUser
from .models import Comment,Post
from django.utils.html import strip_tags,escape

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
    markdown = forms.BooleanField(required = False, widget=forms.CheckboxInput(
        attrs={
            'class': 'checkbox form-control'
        }
    ))
    imageLink = forms.ImageField(label="Image",required = False)
    # privacy = forms.CharField(label='Privacy', widget=forms.Select(choices=privacyOptions))
    privacy = forms.ChoiceField(widget=forms.Select, choices=privacyOptions, label='Privacy')
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
    friendToAdd = forms.CharField(label="Local Author's Username or Remote Author's ID", max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter a username or user ID...'
        }))
    isRemoteAuthor = forms.BooleanField(label="Add a remote author", required = False, widget=forms.CheckboxInput(
        attrs={
            'class': 'myCheckbox'
        }
    ))

class acceptIgnoreRequestForm(forms.Form):
    # This will simply be a button with an invisible value
    # nvm this might be a stupid idea
    pass


class updatePostForm(forms.ModelForm):
    # Furthermore, a post should require at least a summary or an image
    title = forms.CharField(label='Title', max_length=24, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Post Title...'
        }))
    body = forms.CharField(label='Body', required = False, widget=forms.Textarea(
        attrs={
            'rows':7,
            'class': 'form-control',
            'placeholder': 'Write a post...'
        }))
    markdown = forms.BooleanField(required = False, widget=forms.CheckboxInput(
        attrs={
            'class': 'checkbox form-control'
        }
    ))
    imageLink = forms.ImageField(label="Image",required = False)
    # privacy = forms.CharField(label='Privacy', widget=forms.Select(choices=privacyOptions))
    privacy = forms.ChoiceField(widget=forms.Select, choices=privacyOptions, label='Privacy')
    # If we wanted to get fancy, this could autofill from the user's friends
    sharedAuthor = forms.CharField(label='Shared Author', required = False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Shared Author?...'
        }))
    class Meta:
        model = Post
        fields = ['title', 'body', 'markdown', 'image_link','shared_author']
        
    def save(self, post=None):
        post_up = super(updatePostForm, self).save(commit=False)
        if post:
            # print("true")
            post_up = post 
        # print(" no true")
        if "<script>" in post_up.body or "</script>" in post_up.body:
            post_up.body = escape(post_up.body)  
        post_up.save()
        return post_up
  
class EditProfileForm(forms.ModelForm):

    displayname = forms.CharField(label='New Display Name', max_length=24, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter Display Name...'
        }))
    first_name = forms.CharField(label='New First Name', max_length=24, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter a First Name...'
        }))

    last_name = forms.CharField(label='New Last Name', max_length=24, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter a Last Name...'
        }))
    bio = forms.CharField(label='Bio', required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter a bio...'
        }))
    email = forms.CharField(label='New Email', required=False, widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter email...'
        }))
    github_id = forms.CharField(label='Github Username', max_length=24, required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Your Github Username'
        }))
    github_url = forms.CharField(label='Github URL', required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'https://github.com/yourgithubid'
        }))
    class Meta:
        model = CustomUser
        fields = ['displayname', 'first_name', 'last_name', 'bio', 'email', 'github_id','github_url']
        
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
