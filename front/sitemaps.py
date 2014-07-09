from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from front.models import Startup, Job, Person


class StaticSitemap(Sitemap):
    lastmod = None

    def items(self):
        return [
            (reverse('home'), 'daily'),
            (reverse('about'), 'daily'),
            #reverse('who'),
            (reverse('startups_index'), 'daily'),
            (reverse('jobs_index'), 'daily'),
            (reverse('people_index'), 'daily'),
            reverse('login'),
            reverse('startups_create'),
            reverse('logout'),
            reverse('password_change'),
            reverse('password_reset')]

    def changefreq(self, obj):
        return obj[1] if isinstance(obj, tuple) else 'monthly'

    def location(self, obj):
        return obj[0] if isinstance(obj, tuple) else obj


class StartupsSitemap(Sitemap):
    changefreq = 'daily'

    def items(self):
        return Startup.objects.all()

    def lastmod(self, obj):
        return obj.updated


class JobsSitemap(Sitemap):
    changefreq = 'daily'

    def items(self):
        return Job.active.all()

    def lastmod(self, obj):
        return obj.updated


class PeopleSitemap(Sitemap):
    changefreq = 'daily'

    def items(self):
        return Person.objects.all()

    def lastmod(self, obj):
        return obj.updated
