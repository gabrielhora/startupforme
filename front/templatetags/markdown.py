from django.utils.safestring import mark_safe
from django import template
# to import a module with same name use __import__
py_markdown = __import__('markdown')


register = template.Library()

@register.filter(name='markdown')
def markdown_filter(value):
    return mark_safe(py_markdown.markdown(value, extensions=['nl2br']))

markdown_filter.is_safe = True