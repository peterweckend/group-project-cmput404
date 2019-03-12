from django import forms

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
    ("6","Public")]

class uploadForm(forms.Form):
    # Need an invisible field that sends the user ID
    # Alternatively could just post infer it when the user posts the form in the view
    # Furthermore, a post should require at least a summary or an image
    title = forms.CharField(label='Title', max_length=24)
    body = forms.CharField(label='Body', max_length=100, required = False)
    markdown = forms.BooleanField(required = False)
    image = forms.ImageField(label="Image",required = False)
    imageLink = forms.CharField(label='Image Link', max_length=100, required = False)
    privacy = forms.CharField(label='Privacy', widget=forms.Select(choices=privacyOptions))
    # If we wanted to get fancy, this could autofill from the user's friends
    sharedAuthor = forms.CharField(label='Shared Author', required = False)
    pass
