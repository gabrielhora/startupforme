from django import template
from front.models import Startup
from django.core.urlresolvers import reverse
from front.templatetags.utils import remove_http


register = template.Library()


def get_other_startups(parser, token):
    try:
        func, count = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r' % token.split_contents()[0])
    return OtherStartupsNode(count)

get_other_startups = register.tag(get_other_startups)


class OtherStartupsNode(template.Node):
    def __init__(self, count):
        self.count = count
    
    def render(self, context):
        random_startups = Startup.objects.select_related().order_by('?')[:self.count]
        items = u''
        item_html = u"""
        <div>
            <div><a href="%s" style="color:#34495e">%s</a></div>
            <a href="%s" target="_blank">%s</a>
        </div>
        <hr style="margin:10px 0;">
        """

        for startup in random_startups:
            items += item_html % (
                reverse('startups_details', args=[startup.owner.username]), 
                startup.name,
                startup.site, 
                remove_http(startup.site, 25)
            )
        
        return u'<div class="other_jobs">%s</div>' % items
