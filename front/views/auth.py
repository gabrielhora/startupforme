# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as _login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import logout_then_login

def login(request):
    """
    the user can login with either the username or password
    behind the scenes we always use the username
    """
    if request.GET.get('next'):
        request.session['next'] = request.GET.get('next')
    next = request.session.get('next', reverse('home'))
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if '@' in username and '.' in username:
            # username is an email, find the real username
            try:
                user = User.objects.get(email=username)
                username = user.username
            except: 
                pass # if not found the authenticate will not work
        
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            _login(request, user)
            messages.success(request, 'Bem-vindo!')
            request.session['next'] = None
            return redirect(next)
        else:
            messages.error(request, 'Usuário ou senha inválidos')
            return redirect(reverse('login'))
    return render(request, 'front/auth/login.html', {'title': 'Login'})


def logout(request):
    if request.user.is_authenticated:
        messages.success(request, u'Até logo, %s!' % request.user.username)
    return logout_then_login(request, login_url=reverse('login'))
