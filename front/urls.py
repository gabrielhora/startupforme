from django.conf.urls import patterns, url

from front.views import *

urlpatterns = patterns('',
    url(r'^$', home.index, name='home'),
    url(r'^sobre/$', home.about, name='about'),
    #url(r'^quem-somos/$', home.who, name='who'),
    
    # startups
    url(r'^startups/$', startups.index, name='startups_index'),
    
    # jobs
    url(r'^vagas/$', jobs.index, name='jobs_index'),
    url(r'^vagas/criar/$', jobs.create, name='jobs_create'),
    url(r'^vagas/preview/(?P<slug>[-\w]+)/$', jobs.preview, name='jobs_preview'),
    url(r'^vagas/publicar/(?P<slug>[-\w]+)/$', jobs.publish, name='jobs_publish'),
    url(r'^vagas/cancelar/(?P<slug>[-\w]+)/$', jobs.cancel, name='jobs_cancel'),
    url(r'^vagas/excluir/(?P<slug>[-\w]+)/$', jobs.delete, name='jobs_delete'),
    url(r'^vagas/editar/(?P<slug>[-\w]+)/$', jobs.edit, name='jobs_edit'),
    url(r'^vagas/(?P<slug>[-\w]+)/$', jobs.details, name='jobs_details'),

    # people
    url(r'^pessoas/$', people.index, name='people_index'),
    url(r'^pessoas/autorizar/$', people.authorize, name='people_authorize'),
    url(r'^pessoas/autorizado/$', people.authorized, name='people_authorized'),
    url(r'^pessoas/deletar/(?P<slug>[-\w]+)/$', people.delete, name='people_delete'),
    url(r'^pessoas/atualizar/(?P<slug>[-\w]+)/$', people.update, name='people_update'),
    url(r'^pessoas/(?P<slug>[-\w]+)/$', people.profile, name='people_profile'),
    
    # auth
    url(r'^login/$', auth.login, name='login'),
    url(r'^cadastre/$', startups.create, name='startups_create'),
    url(r'^logout/$', auth.logout, name='logout'),
    
    url(r'^mudar-senha/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^mudar-senha/ok/$', 'django.contrib.auth.views.password_change_done'),
    
    url(r'^recuperar-senha/$', 'django.contrib.auth.views.password_reset', {'post_reset_redirect': '/recuperar-senha/ok/'}, name='password_reset'),
    url(r'^recuperar-senha/ok/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^recuperar-senha/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect': '/recuperar-senha/pronto/'}),
    url(r'^recuperar-senha/pronto/$', 'django.contrib.auth.views.password_reset_complete'),
    
    # startup profile page
    url(r'^(?P<username>[-\w]+)/$', startups.details, name='startups_details'),
    url(r'^editar/(?P<username>[-\w]+)/$', startups.edit, name='startups_edit'),
    url(r'^excluir/(?P<username>[-\w]+)/$', startups.delete, name='startups_delete'),
)
