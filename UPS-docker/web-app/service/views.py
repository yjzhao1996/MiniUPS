from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from .format.form import *
from .models import account
from .database_search import *

# Create your views here.
"""
def login_view(request, *args, **kwargs):
    return render(request, 'login.html', {})
"""

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('waiting_packages_view', args=[user.id]))
            else:
                  return render(request, 'login.html', {'form': form,
                               'message': 'Wrong password. Please try again.'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def regist_view(request):
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            #name = form.cleaned_data['name']
            #phone=form.cleaned_data['phone']
            user = User.objects.create_user(username=username, password=password, email=email)
            #return HttpResponseRedirect(reverse('login_index'))
            acc=account(user=user,username=username,email=email)
            acc.save()
            #form1 = LoginForm()
            #return render(request, 'login.html', {'form': form1})
            return redirect('login_view')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def waiting_packages_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    packages=search_waiting_packages(user.username)
    return render(request, 'contact.html', {'packages': packages, 'pk': pk })

@login_required
def loading_packages_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    packages=search_loading_packages(user.username)
    return render(request, 'contact.html', {'packages': packages, 'pk': pk })

@login_required
def delivering_packages_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    packages=search_delivering_packages(user.username)
    return render(request, 'contact.html', {'packages': packages, 'pk': pk })

@login_required
def delivered_packages_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    packages=search_delivered_packages(user.username)
    return render(request, 'contact.html', {'packages': packages, 'pk': pk })
    
@login_required
def packages_info_view(request, pk ,id):
    if request.method == 'POST':

        form = CDForm(request.POST)
        if form.is_valid():
            d_x=form.cleaned_data['d_x']
            d_y=form.cleaned_data['d_y']
            change_destination(id,d_x,d_y)
            return redirect('packages_view', pk=pk)
    else:
        form = CDForm()

    return render(request, 'change_dest.html', {'form': form, 'pk':pk})

@login_required
def sign_out_view(request):
    auth.logout(request)
    return redirect('login_view')

def home_view(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']
            return redirect('package_view', id=id)
    else:
        form = SearchForm()

    return render(request, 'home.html', {'form': form})

def package_view(request,id):
    package=search_package(id)
    return render(request, 'package.html', {'package': package})
