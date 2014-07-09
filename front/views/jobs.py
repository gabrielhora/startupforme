# -*- coding: utf-8 -*-

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from front.forms import JobForm
from front.models import Startup, Job
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from front.utils import get_paginator, tweet_job, send_mail


def index(request):
    # search parameters
    search = request.GET.get('q')
    startup_owner = request.GET.get('startup')
    tag = request.GET.get('tag')
    startup_state = request.GET.get('estado')

    jobs_list = Job.active.select_related().order_by('-published')
    if startup_owner:
        jobs_list = jobs_list.filter(startup__owner__username=startup_owner)
    if tag:
        jobs_list = jobs_list.filter(tags__name__in=[tag])
    if startup_state:
        jobs_list = jobs_list.filter(startup__state__iexact=startup_state)
    if search:
        jobs_list = jobs_list.filter(Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(experience__icontains=search) |
            Q(education__icontains=search) |
            Q(salary__icontains=search))

    jobs = get_paginator(request, jobs_list)
    return render(request, 'front/jobs/index.html', {'title': 'Vagas', 'jobs': jobs})


@login_required
def create(request):
    form = JobForm()
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            startup = Startup.objects.get(owner=request.user)
            job.startup = startup
            job.save()
            form.save_m2m()
            return redirect(reverse('jobs_preview', args=[job.slug]))

    return render(request, 'front/jobs/create.html', {
        'title': 'Cadastrar Vaga',
        'form': form
    })


@login_required
def edit(request, slug):
    startup = get_object_or_404(Startup.objects.select_related(), owner=request.user)
    job = get_object_or_404(Job.objects.select_related(), slug=slug, startup=startup)

    tags = ', '.join([tag.name for tag in job.tags.all()])
    form = JobForm(initial={'tags': tags}, instance=job)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Vaga %s alterada." % job.title)
            
            # redirect to the right page
            if str(request.GET.get('r')) == 'preview':
                url = reverse('jobs_preview', args=[job.slug])
                print(url)
            else:
                url = reverse('jobs_details', args=[job.slug])
            return redirect(url)
    
    return render(request, 'front/jobs/edit.html', {
        'title': 'Editando %s' % job.title,
        'job': job,
        'form': form
    })


def details(request, slug):
    job = get_object_or_404(Job.active_noexpired.select_related(), slug=slug)
    if job.is_expired():
        messages.info(request, u'A vaga de <b>%s</b> na <b>%s</b> já expirou. Veja nossas outras vagas.' % (job.title, job.startup.name))
        return redirect(reverse('jobs_index'))
    return render(request, 'front/jobs/details.html', {'title': "%s na %s" % (job.title, job.startup.name), 'job': job})


@login_required
def preview(request, slug):
    startup = get_object_or_404(Startup.objects.select_related(), owner=request.user)
    job = get_object_or_404(Job.objects.select_related(), slug=slug, startup=startup, published__isnull=True)
    return render(request, 'front/jobs/preview.html', {'title': "%s na %s" % (job.title, startup.name), 'job': job})


@login_required
def publish(request, slug):
    startup = get_object_or_404(Startup.objects.select_related(), owner=request.user)
    job = get_object_or_404(Job.objects.select_related(), slug=slug, startup=startup, published__isnull=True)
    job.published = datetime.datetime.now()
    job.expire_at = job.published + datetime.timedelta(days=30)
    job.save()
    
    # post on twitter
    tweet_job(request, job)
    
    # send email
    send_mail(startup.owner.email,
              'Vaga %s publicada!' % job.title, 
              'front/email/job_created.txt', 
              {'job': job,
               'job_edit_url': request.build_absolute_uri(reverse('jobs_edit', args=[job.slug])),
               'job_url': request.build_absolute_uri(reverse('jobs_details', args=[job.slug])) })
    
    messages.success(request, "Vaga <b>%s</b> publicada. Compartilhe esta URL!" % job.title)
    return redirect(reverse('jobs_details', args=[job.slug]))


@login_required
def cancel(request, slug):
    startup = get_object_or_404(Startup.objects.select_related(), owner=request.user)
    job = get_object_or_404(Job.objects.select_related(), slug=slug, startup=startup, published__isnull=True)
    job.delete()
    messages.success(request, u'Vaga %s excluída.' % job.title)
    return redirect(reverse('home'))


@login_required
def delete(request, slug):
    startup = get_object_or_404(Startup.objects.select_related(), owner=request.user)
    job = get_object_or_404(Job.active.select_related(), slug=slug, startup=startup)
    job.deleted = datetime.datetime.now()
    job.save()
    messages.success(request, u'Vaga %s excluída.' % job.title)
    return redirect(reverse('home'))





















