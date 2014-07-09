# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from front.models import Startup, Job, Person, Subscriber
from django.contrib import messages
from django.core.urlresolvers import reverse


def index(request):
    startups = Startup.objects.select_related().exclude(logo='').order_by('?')[:6]
    return render(request, 'front/home/index.html', {'startups': startups})


def about(request):
    return render(request, 'front/home/about.html')


def who(request):
    gabriel = Person.objects.get(email='gabrielhora@gmail.com')
#    celso = Person.objects.get(email='horacelso@gmail.com')
#    elmo = Person.objects.get(email='elmocampos@gmail.com')
    josi = Person.objects.get(email='josianepedruzzi@gmail.com')

    people = [gabriel, josi]

    return render(request, 'front/home/who.html', {'people': people})
