# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from front.models import Startup
from front.forms import NewStartupForm, EditStartupForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from front.utils import get_paginator, tweet_startup, send_mail


def index(request):
    # search parameters
    search = request.GET.get('q')
    tag = request.GET.get('tag')
    state = request.GET.get('estado')
    
    startups_list = Startup.objects.select_related().order_by('-created')
    if tag:
        startups_list = startups_list.filter(tags__name__in=[tag])
    if state:
        startups_list = startups_list.filter(state__iexact=state)
    if search:
        startups_list = startups_list.filter(
            Q(name__icontains=search) |
            Q(site__icontains=search) |
            Q(short_profile__icontains=search) |
            Q(profile__icontains=search) |
            Q(address__icontains=search))

    startups = get_paginator(request, startups_list)
    return render(request, 'front/startups/index.html', {'title': 'Startups', 'startups': startups})


def details(request, username):
    startup = get_object_or_404(Startup.objects.select_related(), owner__username=username)

    return render(request, 'front/startups/details.html', {
        'title': startup.name, 
        'startup': startup, 
    })


@login_required
def delete(request, username):
    startup = get_object_or_404(Startup, owner__username=username)
    
    if startup.owner == request.user:
        startup.delete()
        logout(request)
        messages.success(request, u'A startup %s foi excluída com sucesso. Esperamos vê-lo novamente em breve.' % startup.name)
    else:
        messages.error(request, u'Você precisa ser o dono da startup para excluí-la.')
    
    return redirect(reverse('home'))

@login_required
def edit(request, username):
    startup = get_object_or_404(Startup.objects.select_related(), owner__username=username)
    if request.user != startup.owner:
        raise Http404()

    if request.method == 'POST':
        form = EditStartupForm(request.POST, request.FILES, instance=startup)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações atualizadas com sucesso.')
            return redirect(reverse('startups_edit', args=[username]))
    else:
        tags = ', '.join([tag.name for tag in startup.tags.all()])
        form = EditStartupForm(initial={'tags': tags}, instance=startup)

    return render(request, 'front/startups/edit.html', {
        'title': startup.name, 
        'startup': startup, 
        'form': form,
    })


def create(request):
    form = NewStartupForm()
    
    if request.method == 'POST':
        form = NewStartupForm(request.POST)
        
        if form.is_valid():
            # create the user first
            user = User.objects.create_user(
                form.cleaned_data.get('username'), 
                form.cleaned_data.get('email'), 
                form.cleaned_data.get('password')
            )

            # create the startup
            startup = Startup.objects.create(
                owner=user,
                site=form.cleaned_data.get('site'),
                name=form.cleaned_data.get('name'),
                address=form.cleaned_data.get('address'),
                state=form.cleaned_data.get('state')
            )
            
            # tweet the welcome message
            tweet_startup(request, startup)
            
            # send welcome email
            send_mail(startup.owner.email,
                      'Bem-vindo ao StartupForMe!', 
                      'front/email/startup_welcome.txt', 
                      {'startup': startup, 
                       'profile_url': request.build_absolute_uri(reverse('startups_details', args=[startup.owner.username])),
                       'edit_profile_url': request.build_absolute_uri(reverse('startups_edit', args=[startup.owner.username])),
                       'jobs_create_url': request.build_absolute_uri(reverse('jobs_create')) })
            
            # login the user
            loggedin_user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            login(request, loggedin_user)

            # done
            messages.success(request, 'Seja bem-vindo, %s! Por favor, complete seu cadastro.' % startup.name)
            return redirect(reverse('startups_edit', args=[startup.owner.username]))

    return render(request, 'front/startups/create.html', {'title': 'Crie sua Startup', 'form': form})










