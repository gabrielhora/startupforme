from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic import TemplateView
from front.sitemaps import StaticSitemap, StartupsSitemap, JobsSitemap, PeopleSitemap

admin.autodiscover()

sitemaps = {
    'front': StaticSitemap,
    'startups': StartupsSitemap,
    'jobs': JobsSitemap,
    'people': PeopleSitemap,
}

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # sitemap & robots
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='front/robots.txt', content_type='text/plain')),

    url(r'^', include('front.urls')),
)
