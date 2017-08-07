# coding: utf-8
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sites.models import Site
from django.views.i18n import set_language
from mezzanine.accounts.views import logout
from mezzanine.blog.models import BlogPost
from mezzanine.conf import settings
from mezzanine.core.views import direct_to_template

from . import views

_slash = '/'

admin.autodiscover()
admin.site.unregister(BlogPost)
admin.site.unregister(Site)

dados_pattern = [
    url(r'^perfil_populacional/$', views.dados_perfil_populacional,
        name='dados_perfil_populacional'),
    url(r'^educacao/$', views.dados_educacao, name='dados_educacao'),
    url(r'^piramide_etaria/$', views.dados_piramide_etaria,
        name='dados_piramide_etaria'),
    url(r'^$', views.dados_home, name='dados_home')
]

# Publicacao patterns.
publicacao_pattern = [
    # url(r'^feeds/(?P<format>.*)%s$' % _slash,
    #     views.publicacao_feed, name='publicacao_feed'),
    #url(r'^tag/(?P<tag>.*)/feeds/(?P<format>.*)%s$' % _slash,
    #    views.publicacao_feed, name='publicacao_feed_tag'),
    url(r'^tag/(?P<tag>.*)%s$' % _slash,
        views.publicacao_list_tag, name='publicacao_list_tag'),
    #url(r'^categoria/(?P<categoria>.*)/feeds/(?P<format>.*)%s$' % _slash,
    #    views.publicacao_feed, name='publicacao_feed_categoria'),
    url(r'^categoria/(?P<categoria>.*)%s$' % _slash,
        views.publicacao_list_categoria, name='publicacao_list_categoria'),
    #url(r'^author/(?P<username>.*)/feeds/(?P<format>.*)%s$' % _slash,
    #    views.publicacao_feed, name='publicacao_feed_author'),
    #url(r'^author/(?P<username>.*)%s$' % _slash,
    #    views.publicacao_list, name='publicacao_list_author'),
    #url(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})%s$' % _slash,
    #    views.publicacao_list, name='publicacao_list_month'),
    #url(r'^archive/(?P<year>\d{4})%s$' % _slash,
    #    views.publicacao_list, name='publicacao_list_year'),
    #url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
    #    '(?P<slug>.*)%s$' % _slash,
    #    views.publicacao_detail, name='publicacao_detail_day'),
    #url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)%s$' % _slash,
    #    views.publicacao_detail, name='publicacao_detail_month'),
    #url(r'^(?P<year>\d{4})/(?P<slug>.*)%s$' % _slash,
    #    views.publicacao_detail, name='publicacao_detail_year'),
    url(r'^(?P<slug>.*)%s$' % _slash, views.publicacao_detail,
        name='publicacao_detail'),
    url(r'^$', views.publicacao_home, name='publicacao_home'),
]

especialistas_pattern = [
    url(r'^area_de_atuacao/(?P<area_de_atuacao>.*)%s$' % _slash,
        views.especialistas_list, name='especialista_list'),
    url(r'^especialidade/(?P<especialidade>.*)%s$' % _slash,
        views.especialistas_list, name='especialista_list'),
    url(r'^(?P<slug>.*)%s$' % _slash, views.publicacao_detail,
        name='publicacao_detail'),
    url(r'^$', views.especialistas_list, name='especialista_list'),
]

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = i18n_patterns(
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    url("^admin/", include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += [
        url('^i18n/$', set_language, name='set_language'),
    ]

urlpatterns += [
    url(r'^[Pp]ublicacoes/', include(publicacao_pattern)),
    url(r'^[Ee]specialistas/', include(especialistas_pattern)),
    url(r'^[Dd]ados/', include(dados_pattern)),
    url(r'^entrar/$', views.login_user),
    url(r'^sair/$', logout),
    url(r'^cadastro/$', views.register_user),
    url(r'^recuperar_senha/$', views.password_recovery),
    url(r'^painel_dados/$', views.data_dashboard),
    # We don't want to presume how your homepage works, so here are a
    # few patterns you can use to set it up.

    # HOMEPAGE AS STATIC TEMPLATE
    # ---------------------------
    # This pattern simply loads the index.html template. It isn't
    # commented out like the others, so it's the default. You only need
    # one homepage pattern, so if you use a different one, comment this
    # one out.

    url("^$", direct_to_template, {"template": "index.html"}, name="home"),

    # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
    # ---------------------------------------------
    # This pattern gives us a normal ``Page`` object, so that your
    # homepage can be managed via the page tree in the admin. If you
    # use this pattern, you'll need to create a page in the page tree,
    # and specify its URL (in the Meta Data section) as "/", which
    # is the value used below in the ``{"slug": "/"}`` part.
    # Also note that the normal rule of adding a custom
    # template per page with the template name using the page's slug
    # doesn't apply here, since we can't have a template called
    # "/.html" - so for this case, the template "pages/index.html"
    # should be used if you want to customize the homepage's template.
    # NOTE: Don't forget to import the view function too!

    # url("^$", mezzanine.pages.views.page, {"slug": "/"}, name="home"),

    # HOMEPAGE FOR A BLOG-ONLY SITE
    # -----------------------------
    # This pattern points the homepage to the blog post listing page,
    # and is useful for sites that are primarily blogs. If you use this
    # pattern, you'll also need to set BLOG_SLUG = "" in your
    # ``settings.py`` module, and delete the blog page object from the
    # page tree in the admin if it was installed.
    # NOTE: Don't forget to import the view function too!

    # url("^$", mezzanine.blog.views.blog_post_list, name="home"),

    # MEZZANINE'S URLS
    # ----------------
    # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!

    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.
    url("^", include("mezzanine.urls")),

    # MOUNTING MEZZANINE UNDER A PREFIX
    # ---------------------------------
    # You can also mount all of Mezzanine's urlpatterns under a
    # URL prefix if desired. When doing this, you need to define the
    # ``SITE_PREFIX`` setting, which will contain the prefix. Eg:
    # SITE_PREFIX = "my/site/prefix"
    # For convenience, and to avoid repeating the prefix, use the
    # commented out pattern below (commenting out the one above of course)
    # which will make use of the ``SITE_PREFIX`` setting. Make sure to
    # add the import ``from django.conf import settings`` to the top
    # of this file as well.
    # Note that for any of the various homepage patterns above, you'll
    # need to use the ``SITE_PREFIX`` setting as well.

    # ("^%s/" % settings.SITE_PREFIX, include("mezzanine.urls"))

    url("^", include("mezzanine.accounts.urls")),
]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
