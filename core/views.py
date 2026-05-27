from traceback import print_tb
from urllib.request import Request

from django.contrib.auth.templatetags import auth
from django.core.management.commands import flush
from django.db.models import Model
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.urls import reverse
from faker.providers.sbn import RegistrantRule


from .models import Profile
from core.forms import LoginForm, SignUpForm, UserForm, ProfileForm


# Create your views here.
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = auth.authenticate(username=username,password=password)

            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                form.add_error(None, 'Invalid login/password')
    else:
        form = LoginForm()
    return render(request,'core/login.html',{'form' : form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = SignUpForm()
    return render(request,'core/signup.html', {'form' : form})

def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=request.user)
        form_profile = ProfileForm(request.POST, request.FILES, instance=profile)
        if form_user.is_valid() and form_profile.is_valid():
            form_user.save()
            form_profile.save()

            return HttpResponseRedirect(reverse('core:profile'))
    else:
        form_user = UserForm(instance=request.user)
        form_profile = ProfileForm(instance=profile)
        return render(request,'core/profile.html', {'form_user' : form_user, 'form_profile' : form_profile})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))

