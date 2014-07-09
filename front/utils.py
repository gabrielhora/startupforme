# -*- coding: utf-8 -*-
from django.core.mail.message import EmailMultiAlternatives

from twitter import Twitter, OAuth
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template.context import Context
from django.core.mail import send_mail as dj_send_mail, get_connection


states = (
    ('', u'Escolha'),
    ('AC', u'Acre'),
    ('AL', u'Alagoas'),
    ('AP', u'Amapá'),
    ('AM', u'Amazonas'),
    ('BA', u'Bahia '),
    ('CE', u'Ceará'),
    ('DF', u'Distrito Federal '),
    ('ES', u'Espírito Santo'),
    ('GO', u'Goiás'),
    ('MA', u'Maranhão'),
    ('MT', u'Mato Grosso'),
    ('MS', u'Mato Grosso do Sul'),
    ('MG', u'Minas Gerais'),
    ('PA', u'Pará'),
    ('PB', u'Paraíba'),
    ('PR', u'Paraná'),
    ('PE', u'Pernambuco'),
    ('PI', u'Piauí'),
    ('RJ', u'Rio de Janeiro'),
    ('RN', u'Rio Grande do Norte'),
    ('RS', u'Rio Grande do Sul'),
    ('RO', u'Rondônia'),
    ('RR', u'Roraima'),
    ('SC', u'Santa Catarina'),
    ('SP', u'São Paulo'),
    ('SE', u'Sergipe'),
    ('TO', u'Tocantins'),
)


def get_paginator(request, list):
    paginator = Paginator(list, settings.RECORDS_PER_PAGE)
    page = request.GET.get('p')
    
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    
    return result


def send_mail(to, subject, template, context={}, html=False):
    #if settings.DEBUG:
    #    return
    
    email_template = get_template(template)
    c = Context(context)
    from_email, subject_prefix = settings.DEFAULT_FROM_EMAIL, settings.EMAIL_SUBJECT_PREFIX

    connection = get_connection(fail_silently=True)
    
    message = EmailMultiAlternatives(subject=subject_prefix + subject,
                                     body=email_template.render(c), 
                                     from_email=from_email, 
                                     to=[to], 
                                     connection=connection,
                                     headers={'Reply-To': 'StartupForMe <contato@example.com>'})

    if html:
        message.attach_alternative(email_template.render(c), 'text/html')
        message.html = email_template.render(c)
        message.auto_html = True
        message.content_subtype = "html"

    message.send()


def get_twitter():
    return Twitter(auth=OAuth(settings.TWITTER_OAUTH_TOKEN, 
        settings.TWITTER_OAUTH_SECRET,
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET))


def tweet(status):
    if settings.DEBUG:
        return # do not tweet on debug mode
    
    return get_twitter().statuses.update(status=status)


def tweet_job(request, job):
    if settings.DEBUG:
        return # do not tweet on debug mode
    
    url = request.build_absolute_uri(reverse('jobs_details', args=[job.slug]))
    description = "%s busca %s" % (job.startup.name, job.title)
    if len(description) > settings.TWITTER_MAX_LENGTH:
        description = description[:settings.TWITTER_MAX_LENGTH] + "..."
    return tweet("%s %s" % (description, url))


def tweet_startup(request, startup):
    if settings.DEBUG:
        return # do not tweet on debug mode

    url = request.build_absolute_uri(reverse('startups_details', args=[startup.owner.username]))
    description = "%s, bem-vinda ao #startupforme" % startup.name
    if len(description) > settings.TWITTER_MAX_LENGTH:
        description = description[:settings.TWITTER_MAX_LENGTH] + "..."
    return tweet("%s %s" % (description, url))