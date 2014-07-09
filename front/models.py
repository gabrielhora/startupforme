# -*- coding: utf-8 -*-

import uuid
import os
import datetime
import random
from django.conf.urls import patterns, url

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from postmonkey.exceptions import MailChimpException
from taggit.managers import TaggableManager
from imagekit.models.fields import ImageSpecField
from imagekit.processors.resize import ResizeToFill, ResizeToCover
from geopy import geocoders
from geopy.geocoders.googlev3 import GQueryError, GTooManyQueriesError
from front.utils import states, send_mail
from postmonkey import PostMonkey


mailchimp = PostMonkey(settings.MAILCHIMP_APIKEY, datacenter=settings.MAILCHIMP_DATACENTER)


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads', filename)


class DefaultModelAdmin(admin.ModelAdmin):
    def queryset(self, request):
        qs = self.model.default.get_query_set()
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class StartupModelAdmin(DefaultModelAdmin):
    def get_urls(self):
        urls = super(StartupModelAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^gettoknow/$', self.admin_site.admin_view(self.gettoknow), name='gettoknow'),)
        return my_urls + urls

    def gettoknow(self, request):
        if request.method == 'POST':
            email = request.POST['email']
            first_name = request.POST['name']
            last_name = request.POST['last_name']

            result = mailchimp.listMemberInfo(id=settings.MAILCHIMP_LISTID, email_address=email)
            if result['errors'] == 0:
                # it means this email is already on the list
                messages.error(request, "Já mandamos pra este email antes.")
            else:
                # this email is not on the list, add it and send the email
                try:
                    mailchimp.listSubscribe(id=settings.MAILCHIMP_LISTID,
                                            email_address=email,
                                            double_optin=False,
                                            send_welcome=False,
                                            merge_vars={'FNAME': first_name, 'LNAME': last_name})
                    send_mail(email, u'%s Conheça o StartupForMe' % first_name, 'front/email/gettoknow.html', html=True)
                    messages.success(request, "Email enviado.")
                except MailChimpException:
                    messages.error(request, "Deu algum problema no envio, passa pro próximo.")

            return redirect(reverse('admin:gettoknow'))

        return render(request, 'front/startups/gettoknow.html')


class ActiveManager(models.Manager):
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(deleted__isnull=True)


class DeletedManager(models.Manager):
    def get_query_set(self):
        return super(DeletedManager, self).get_query_set().filter(deleted__isnull=False)


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    
    objects = ActiveManager()
    trash = DeletedManager()
    default = models.Manager()
    
    class Meta:
        abstract = True


class Subscriber(BaseModel):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255)

    def __unicode__(self):
        return self.email


class Person(BaseModel):
    slug = models.SlugField(max_length=768)
    linkedin_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=768, null=True, blank=True)
    email = models.CharField(max_length=1024)
    headline = models.TextField(null=True, blank=True)
    num_connections = models.IntegerField()
    num_connections_capped = models.BooleanField()
    num_recommenders = models.IntegerField()
    picture_url = models.URLField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    profile_url = models.URLField(null=True, blank=True)
    specialties = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=1024, null=True, blank=True) # pegar o name do location
    languages = models.TextField(null=True, blank=True) # pegar os names dentro de languages.language
    skills = models.TextField(null=True, blank=True) # pegar os names dentro de skills.values.skill.name

    linkedin_authorization_code = models.CharField(max_length=255)
    linkedin_expires_in = models.IntegerField()
    linkedin_last_authorization_date = models.DateTimeField()

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('people_profile', args=[self.slug])

    def save(self, *args, **kwargs):
        self.full_name = "%s %s" % (self.first_name, self.last_name)
        
        # try to create a simple slug (without the id)
        # if the slug already exists append the id
        
        temp_slug = slugify("%s%s" % (self.first_name, self.last_name))
        try:
            Person.objects.get(slug=temp_slug)
            self.slug = self.linkedin_id
        except Person.DoesNotExist:
            self.slug = temp_slug
        
        super(Person, self).save(*args, **kwargs)

    def all_positions(self):
        return self.position_set.select_related().order_by("-start_date")

    def current_positions(self):
        return self.position_set.select_related().filter(is_current=True)
    
    def past_positions(self):
        return self.position_set.select_related().filter(is_current=False)
    
    def skills_as_list(self):
        return self.skills.split(', ')

    def random_skills(self):
        skills = self.skills_as_list()
        return random.sample(skills, len(skills))


class Education(BaseModel):
    person = models.ForeignKey(Person)
    linkedin_id = models.CharField(max_length=255, null=True, blank=True)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    start_date = models.IntegerField(null=True, blank=True)
    end_date = models.IntegerField(null=True, blank=True)
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.school_name


class LinkedinCompany(BaseModel):
    linkedin_id = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Position(BaseModel):
    person = models.ForeignKey(Person)
    company = models.ForeignKey(LinkedinCompany)
    linkedin_id = models.CharField(max_length=255, null=True, blank=True)
    is_current = models.BooleanField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_date_month = models.IntegerField(null=True, blank=True)
    start_date_year = models.IntegerField(null=True, blank=True)
    end_date_month = models.IntegerField(null=True, blank=True)
    end_date_year = models.IntegerField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return "%s at %s" % (self.title, self.company.name)
    
    def save(self, *args, **kwargs):
        if not self.start_date_year and not self.start_date_month:
            self.start_date = datetime.datetime.now()

        if self.start_date_year and not self.start_date_month:
            self.start_date = datetime.datetime(year=self.start_date_year, month=1, day=1)
        
        if self.start_date_month and self.start_date_year:
            self.start_date = datetime.datetime(year=self.start_date_year, month=self.start_date_month, day=1)
        
        if not self.end_date_year and not self.end_date_month:
            self.end_date = datetime.datetime.now()
        
        if self.end_date_year and not self.end_date_month:
            self.end_date = datetime.datetime(year=self.end_date_year, month=1, day=1)
        
        if self.end_date_month and self.end_date_year:
            self.end_date = datetime.datetime(year=self.end_date_year, month=self.end_date_month, day=1)
        
        super(Position, self).save(*args, **kwargs)


class Startup(BaseModel):
    owner = models.OneToOneField(User)
    site = models.URLField()
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    gmaps_address = models.CharField(max_length=1024, null=True, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    state = models.CharField(max_length=2)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_profile = models.CharField(max_length=140, null=True, blank=True)
    profile = models.TextField(null=True, blank=True)
    
    logo = models.ImageField(upload_to=get_file_path, max_length=255, null=True, blank=True)
    logo_thumbnail = ImageSpecField([ResizeToCover(220, 220)], image_field='logo', format='PNG', options={'quality': 90})
    logo_thumbnail_circle = ImageSpecField([ResizeToFill(60, 60)], image_field='logo', format='PNG', options={'quality': 90})

    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('startups_details', args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        # try to find the address in google maps
        # this should probably be on a background queue later
        try:
            geo = geocoders.GoogleV3()

            state = self.state
            state_name = [s[1] for s in states if s[0] == self.state]
            if len(state_name) > 0:
                state = state_name[0]

            place, (lat, lng) = geo.geocode('%s, %s' % (self.address, state))
            self.gmaps_address = place
            self.lat = lat
            self.lng = lng
        except (GQueryError, GTooManyQueriesError, ValueError):
            self.gmaps_address = None
            self.lat = None
            self.lng = None

        super(Startup, self).save(*args, **kwargs)


class PublishedJobsManager(models.Manager):
    def get_query_set(self):
        return super(PublishedJobsManager, self).get_query_set().filter(deleted__isnull=True, published__isnull=False)


class PublishedNotExpiredJobsManager(models.Manager):
    def get_query_set(self):
        return super(PublishedNotExpiredJobsManager, self).get_query_set().filter(deleted__isnull=True, published__isnull=False, expire_at__gt=datetime.datetime.now())


class Job(BaseModel):
    startup = models.ForeignKey(Startup)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField()
    experience = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    apply = models.TextField()
    salary = models.TextField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)

    active = PublishedNotExpiredJobsManager()
    active_noexpired = PublishedJobsManager()
    tags = TaggableManager(blank=True)
    
    def __unicode__(self):
        return "%s at %s" % (self.title, self.startup.name)

    def get_absolute_url(self):
        return reverse('jobs_details', args=[self.slug])

    def is_expired(self):
        return datetime.datetime.now() > self.expire_at
    
    def save(self, *args, **kwargs):
        if self.id is None:
            super(Job, self).save(*args, **kwargs)
        self.slug = slugify("%d %s %s" % (self.id, self.startup.name, self.title))
        super(Job, self).save(*args, **kwargs)


admin.site.register(Subscriber, DefaultModelAdmin)

admin.site.register(Person, DefaultModelAdmin)
admin.site.register(Education, DefaultModelAdmin)
admin.site.register(LinkedinCompany, DefaultModelAdmin)
admin.site.register(Position, DefaultModelAdmin)

admin.site.register(Startup, StartupModelAdmin)
admin.site.register(Job, DefaultModelAdmin)