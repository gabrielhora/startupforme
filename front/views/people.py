# -*- coding: utf-8 -*-

from linkedin import linkedin
import front.linkedin as my_linkedin
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.core.urlresolvers import reverse
from front.models import Person
from front.utils import get_paginator, send_mail


auth = linkedin.LinkedInAuthentication(
    settings.LINKEDIN_KEY,
    settings.LINKEDIN_SECRET,
    settings.LINKEDIN_RETURN_URL,
    [linkedin.PERMISSIONS.FULL_PROFILE, linkedin.PERMISSIONS.EMAIL_ADDRESS,])

application = linkedin.LinkedInApplication(auth)


def index(request):
    search = request.GET.get('q')
    people_list = Person.objects.select_related().order_by('-created')
    if search:
        people_list = people_list.filter(
            Q(full_name__icontains=search) |
            Q(headline__icontains=search) |
            Q(interests__icontains=search) |
            Q(summary__icontains=search) |
            Q(location__icontains=search) |
            Q(skills__icontains=search) |
            Q(specialties__icontains=search))
    people = get_paginator(request, people_list)
    return render(request, 'front/people/index.html', {'title': 'Pessoas', 'people': people})
    

def delete(request, slug):
    person = get_object_or_404(Person, slug=slug)
    request.session['linkedin_action'] = my_linkedin.ACTION_DELETE
    request.session['linkedin_id'] = person.linkedin_id
    return redirect("%s?action=%s" % (reverse('people_authorize'), my_linkedin.ACTION_DELETE))


def update(request, slug):
    person = get_object_or_404(Person, slug=slug)
    request.session['linkedin_action'] = my_linkedin.ACTION_UPDATE
    request.session['linkedin_id'] = person.linkedin_id
    return redirect("%s?action=%s" % (reverse('people_authorize'), my_linkedin.ACTION_UPDATE)) 
    

def authorize(request):
    action = request.GET.get('action')
    if action: 
        request.session['linkedin_action'] = request.GET.get('action')
    else:
        request.session['linkedin_action'] = my_linkedin.ACTION_IMPORT
    return redirect(auth.authorization_url)


def authorized(request):
    if request.GET.get('error'):
        messages.error(request, 'Ocorreu um erro ao autorizar seu Linkedin, tente mais tarde')
        return redirect(reverse('startups_create'))

    authorization_code = request.GET.get('code')
    auth.authorization_code = authorization_code
    auth.get_access_token()
    
    # start importing the user profile
    
    linkedin_profile = application.get_profile(selectors=[
        # basic
        'id', 'first-name', 'last-name', 'headline', 'location', 'num-connections', 'num-connections-capped', 'num-recommenders', 
        'summary', 'specialties', 'positions', 'picture-url', 'public-profile-url',
        # email
        'email-address',
        # full profile
        'languages', 'educations', 'skills', 'interests',
    ], headers={'Accept-Language': 'pt-BR,en-US'})
    
    # check what to do after authorization

    action = request.session.get('linkedin_action')

    if action == my_linkedin.ACTION_IMPORT:
        # import
        person = my_linkedin.save(linkedin_profile, auth.token)
        
        # send email
        send_mail(person.email,
                  'Bem-vindo ao StartupForMe!', 
                  'front/email/person_welcome.txt', 
                  {'person': person, 
                   'profile_url': request.build_absolute_uri(reverse('people_profile', args=[person.slug])),
                   'update_profile_url': request.build_absolute_uri(reverse('people_update', args=[person.slug])) })

        # done
        messages.success(request, u'Olá %s, seu perfil foi criado.' % person.first_name)
        return redirect(reverse('people_profile', args=[person.slug]))

    if action == my_linkedin.ACTION_UPDATE:
        linkedin_id = request.session.get('linkedin_id')
        person = get_object_or_404(Person, linkedin_id=linkedin_id)
        
        if linkedin_profile.get('id') == linkedin_id:
            person = my_linkedin.save(linkedin_profile, auth.token)
            messages.success(request, u"Seu perfil foi atualizado.")
            return redirect(reverse('people_profile', args=[person.slug]))
        else:
            messages.error(request, u"Ei! Você não parece ser %s." % person.full_name)
            return redirect(reverse('people_profile', args=[person.slug]))

    if action == my_linkedin.ACTION_DELETE:
        # delete
        linkedin_id = request.session.get('linkedin_id')
        person = get_object_or_404(Person, linkedin_id=linkedin_id)
        
        if linkedin_profile.get('id') == linkedin_id:
            my_linkedin.delete(linkedin_profile)
            messages.success(request, u"Seu perfil foi excluído. Até a próxima.")
            return redirect(reverse('people_index'))
        else:
            messages.error(request, u"Erro ao excluir seu perfil, você não parece ser %s." % person.full_name)
            return redirect(reverse('people_profile', args=[person.slug]))

    # clear linkedin sessions
    request.session['linkedin_action'] = None
    request.session['linkedin_id'] = None

    # should not get here, but anyway
    messages.error(request, "Erro ao excluir seu perfil, tente novamente mais tarde.")
    return redirect(reverse('home'))


def profile(request, slug):
    person = get_object_or_404(Person, slug=slug)
    # get other 5 random people to show in the sidebar
    random_people = Person.objects.order_by('?')[:5]
    return render(request, 'front/people/profile.html', {
        'title': "%s %s" % (person.full_name, person.headline), 
        'person': person,
        'random_people': random_people})



































