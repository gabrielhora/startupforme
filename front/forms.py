# -*- coding: utf-8 -*-

import re

from django import forms
from django.core import validators
from django.contrib.auth.models import User
from django.conf import settings
from taggit.forms import TagField

from front.models import Startup, Job
from front.utils import states



# Little helpers


def my_widget(widget, klass='', placeholder='', validators=''):
    return widget(attrs={'class': "%s %s" % (klass, validators), 'placeholder': placeholder})


def normal_size(widget, placeholder='', validators=''):
    return my_widget(widget, '', placeholder, validators)


def span1(widget, placeholder='', validators=''):
    return my_widget(widget, 'span1', placeholder, validators)


def span3(widget, placeholder='', validators=''):
    return my_widget(widget, 'span3', placeholder, validators)


def span5(widget, placeholder='', validators=''):
    return my_widget(widget, 'span5', placeholder, validators)


def span8(widget, placeholder='', validators=''):
    return my_widget(widget, 'span8', placeholder, validators)


def default(label, field=forms.CharField, widget=forms.TextInput, placeholder='', size=span5,
            client_validators='required', **kwargs):
    if isinstance(widget, forms.Widget):
        form_widget = widget
    else:
        form_widget = size(widget, placeholder, client_validators)
    return field(label=label, widget=form_widget, **kwargs)

# Forms


class NewStartupForm(forms.Form):
    username = default('Usuário *',
                       client_validators='required username',
                       placeholder='http://startupfor.me/SEU_USUÁRIO',
                       help_text='Normalmente o nome da sua empresa <b>sem acentos e sem espaços</b>.')
    email = default('Email *',
                    help_text='Seu email <b>nunca</b> será compartilhado com ninguém.',
                    client_validators='required email',
                    validators=[validators.validate_email])
    password = default('Senha *', widget=forms.PasswordInput, size=span3)
    password_confirmation = default('Confirme a Senha *', widget=forms.PasswordInput, size=span3)

    name = default('Nome da Startup *')
    site = default('Site *', field=forms.URLField, client_validators='required cleanUrl')
    address = default('Endereço *', help_text='Para encontrarmos sua empresa no <b>Google Maps</b>.')
    state = default('Estado *', field=forms.ChoiceField, widget=forms.Select, size=span3, choices=states)

    def clean_email(self):
        """ Email must not be already in use """
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("Email já está sendo usado.")
        return email

    def clean_username(self):
        user = self.cleaned_data['username']

        # check if it contains only allowed characters
        if re.match(r'^[a-z0-9_-]{3,255}$', user) is None:
            raise forms.ValidationError("Formato de usuário inválido, use apenas letras, números, traço ou underline.")

        # check if it is not a reserved word
        if user in settings.INVALID_STARTUP_NAMES:
            raise forms.ValidationError("Você não pode usar este nome de usuário.")

        # check if it is unique
        if User.objects.filter(username=user).exists():
            raise forms.ValidationError("Usuário já está sendo usado.")

        return user

    def clean(self):
        cleaned_data = super(NewStartupForm, self).clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('password_confirmation')

        if password != confirm:
            raise forms.ValidationError("Senhas não conferem")

        return cleaned_data


class EditStartupForm(forms.ModelForm):
    name = default('Nome da Startup *')
    site = default('Site *', field=forms.URLField, client_validators='required cleanUrl')
    short_profile = forms.CharField(
        label='Bio',
        required=False,
        widget=forms.Textarea(attrs={'rows': '2', 'class': 'span7', 'maxlength': '140'}),
        help_text='Um pouco sobre a startup (<b>140</b> caracteres).'
    )
    profile = default('Perfil',
                      widget=forms.Textarea,
                      size=span8,
                      client_validators='',
                      required=False,
                      help_text='Perfil completo da startup, motivações, história, qualquer coisa que quiser.<br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')
    tags = default('Tags',
                   field=TagField,
                   client_validators='',
                   required=False,
                   help_text='Palavras chave relacionadas à startup <b>separadas por vírgula</b>.')
    address = default('Endereço *', help_text='Para encontrarmos sua empresa no <b>Google Maps</b>.')
    state = default('Estado *', field=forms.ChoiceField, widget=forms.Select, size=span3, choices=states)

    class Meta:
        model = Startup
        fields = ('name', 'site', 'tags', 'short_profile', 'profile', 'logo', 'tags', 'address', 'state',)
        exclude = ('owner', 'tags', 'slug',)


class JobForm(forms.ModelForm):
    title = default('Título *', size=span8)
    tags = default('Tags *',
                   field=TagField,
                   help_text="""
        Palavras chave relacionadas à vaga <b>separadas por vírgula</b>.<br/>
        As tags são usadas para caracterizar melhor sua vaga, por exemplo:<br/>
        <i>tecnologia, webdesign</i> ou <i>jornalismo, editoração</i> ou <i>analista, rh</i> esse tipo de coisa.
        """)
    description = default('Descrição *',
                          widget=forms.Textarea,
                          size=span8,
                          help_text='Descrição detalhada da vaga, o que se espera do candidato e o que esperar dele(a).<br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')
    experience = default('Experiência',
                         widget=forms.Textarea(attrs={'class': 'span8', 'rows': '4'}),
                         required=False,
                         help_text='Experiência profissional exigida para a vaga.<br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')
    education = default('Educação',
                        widget=forms.Textarea(attrs={'class': 'span8', 'rows': '4'}),
                        required=False,
                        help_text='Nível de ensino, certificações ou títulos exigidos para a vaga.<br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')
    salary = default('Remuneração & Benefícios',
                     widget=forms.Textarea(attrs={'class': 'span8', 'rows': '4'}),
                     required=False,
                     help_text='O que você oferece para o candidato.<br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')
    apply = default('Como se candidatar *',
                    widget=forms.Textarea(attrs={'class': 'span8 required', 'rows': '4'}),
                    help_text='O que o candidato deve fazer para se candidatar à vaga?<br/>Ex: <i>Envie um email com seu currículo para rh@empresa.com.br</i><br/>Você pode usar <a href="#" class="markdown_help">Markdown</a> aqui.')

    class Meta:
        model = Job
        fields = ('title', 'tags', 'description', 'apply', 'experience', 'education', 'salary',)
        exclude = ('startup', 'slug', 'published',)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
