from django import template
from urllib import unquote
from django.template.defaultfilters import stringfilter, truncatechars
import hashlib


register = template.Library()


@register.filter
def unquote_raw(value):
    return unquote(value)


@register.filter(is_safe=True)
@stringfilter
def remove_http(value, truncate_chars=None):
    result = value.strip()

    # remove protocol
    if result[:8] == 'https://':
        result = result[8:]
    if result[:7] == 'http://':
        result = result[7:]
    if result[:6] == 'ftp://':
        result = result[6:]

    # remove last slash
    if result[-1] == '/':
        result = result[:-1]

    # truncate chars
    if truncate_chars is not None:
        return truncatechars(result, truncate_chars)

    return result
