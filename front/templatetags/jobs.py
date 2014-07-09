from django import template
from front.models import Job
from django.core.urlresolvers import reverse


register = template.Library()


def get_other_jobs(parser, token):
    try:
        func, count = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])
    return OtherJobsNode(count)

get_other_jobs = register.tag(get_other_jobs)


class OtherJobsNode(template.Node):
    def __init__(self, count):
        self.count = count
    
    def render(self, context):
        random_jobs = Job.active.select_related().order_by('?')[:self.count]
        items = u''
        item_html = u"""
        <div>
            <div><a href="%s" style="color:#34495e">%s</a></div>
            <a href="%s">%s</a>
        </div>
        <hr style="margin:10px 0;">
        """

        for job in random_jobs:
            items += item_html % (
                reverse('jobs_details', args=[job.slug]), 
                job.title, 
                reverse('startups_details', args=[job.startup.owner.username]), 
                job.startup.name
            )
        
        return u'<div class="other_jobs">%s</div>' % items
