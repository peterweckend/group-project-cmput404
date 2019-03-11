from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from .forms import uploadForm

def uploadView(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = uploadForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # Here is 
            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = uploadForm()

    return render(request, 'upload/upload.html', {'form': form})