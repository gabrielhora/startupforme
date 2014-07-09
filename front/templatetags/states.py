from django.utils.safestring import mark_safe
from django import template
from django.template.defaultfilters import striptags
from front.utils import states
from front.models import Startup


register = template.Library()


@register.filter(name='state_name')
def state_name_filter(value):
    try:
        return mark_safe(dict(states)[value])
    except KeyError:
        return mark_safe(value)

state_name_filter.is_safe = True


@register.filter(name='startup_name')
def startup_name_filter(value):
    try:
        startup = Startup.objects.get(owner__username=value)
        return mark_safe(startup.name)
    except:
        return value

startup_name_filter.is_safe = True