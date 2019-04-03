from django.shortcuts import render, render_to_response
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages

from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    
    def form_valid(self, form):
        #save cleaned post data
        super().form_valid(form)
        clean = form.cleaned_data
        self.object = form.save()
        messages.info(self.request,"Admin needs to approve user before logging in")
        return super(SignUp, self).form_valid(form)