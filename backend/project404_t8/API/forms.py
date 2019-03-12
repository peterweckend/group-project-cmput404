from django import forms

# This must support markdown
# Maybe have a button that tells the post to display it in markdown
privacyOptions = [("Just Me", "Just Me"), ("Friends","Friends"), ("Friends of Friends", "Friends of Friends"), ("Everyone","Everyone")]#,"Friends","Friends of Friends","Public"]
class uploadForm(forms.Form):
    # Need an invisible field that sends the user ID
    # Alternatively could just post infer it when the user posts the form in the view
    content = forms.CharField(label='Summary', max_length=100)
    # image = forms.FileField()
    privacy = forms.CharField(label='Privacy', widget=forms.Select(choices=privacyOptions))

