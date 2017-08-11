# coding: utf-8
from __future__ import unicode_literals
import json
import base64

from calendar import month_name

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.messages import info, error
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.template import RequestContext
from future.builtins import int, str
from mezzanine.accounts import get_profile_form
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.email import send_verification_mail, send_approve_mail
from mezzanine.utils.views import paginate
from mezzanine.utils.urls import login_redirect, next_url
from bokeh.embed import autoload_server

from .models import AreaDeAtuacao, Especialidade, Especialista, Publicacao

# from mezzanine.utils.views import render

User = get_user_model()


# def setlanguage(request):
    # return render(request, 'set-language.html',
                  # {'LANGUAGES':settings.LANGUAGES,
                   # 'SELECTEDLANG':request.LANGUAGE_CODE})

def publicacao_home(request):
    """Display the Publicações Home page, which is a matrix with all available
    categories (only categories, not the items from the Publicação Class).
    """
    categorias = AreaDeAtuacao.objects.all()
    categorias = categorias.order_by('ordem')
    templates = ["carceropolis/publicacao/publicacao_home.html"]
    context = {'categorias': categorias}
    return TemplateResponse(request, templates, context)


def publicacao_list_tag(request, tag, extra_context=None):
    """Display a list of blog posts that are filtered by tag, year, month,
    author or categoria. Custom templates are checked for using the name
    ``carceropolis/publicacao/publicacao_list_XXX.html`` where ``XXX`` is
    either the categoria slug or author's username if given.
    """
    templates = []
    template = "carceropolis/publicacao/publicacao_list.html"
    publicacoes = Publicacao.objects.published()
    tag = get_object_or_404(Keyword, slug=tag)
    publicacoes = publicacoes.filter(keywords__keyword=tag)

    prefetch = ("categorias", "keywords__keyword")
    publicacoes = publicacoes.prefetch_related(*prefetch)
    publicacoes = paginate(publicacoes, request.GET.get("page", 1),
                           settings.PUBLICACAO_PER_PAGE,
                           settings.MAX_PAGING_LINKS)
    context = {"publicacoes": publicacoes, "tag": tag,}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def publicacao_list_categoria(request, categoria, tag=None, year=None,
                              month=None, username=None, extra_context=None):
    """Display a list of blog posts that are filtered by tag, year, month,
    author or categoria. Custom templates are checked for using the name
    ``carceropolis/publicacao/publicacao_list_XXX.html`` where ``XXX`` is
    either the categoria slug or author's username if given.
    """
    templates = []
    template = "carceropolis/publicacao/publicacao_list.html"
    publicacoes = Publicacao.objects.published()
    categoria = get_object_or_404(AreaDeAtuacao, slug=categoria)
    publicacoes = publicacoes.filter(categorias__nome__in=[categoria])
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        publicacoes = publicacoes.filter(keywords__keyword=tag)
    if year is not None:
        publicacoes = publicacoes.filter(publish_date__year=year)
        if month is not None:
            publicacoes = publicacoes.filter(publish_date__month=month)
            try:
                month = month_name[int(month)]
            except IndexError:
                raise Http404()
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        publicacoes = publicacoes.filter(user=author)
        # templates.append(u"carceropolis/publicacao/publicacao_list_%s.html" %
        #                  username)

    prefetch = ("categorias", "keywords__keyword")
    publicacoes = publicacoes.prefetch_related(*prefetch)
    publicacoes = paginate(publicacoes, request.GET.get("page", 1),
                           settings.PUBLICACAO_PER_PAGE,
                           settings.MAX_PAGING_LINKS)
    context = {"publicacoes": publicacoes, "year": year, "month": month,
               "tag": tag, "categoria": categoria, "author": author}
    context.update(extra_context or {})
    templates.append(template)
    return TemplateResponse(request, templates, context)


def publicacao_detail(request, slug, extra_context=None):
    """Presenting a specific publication (publicaço)."""
    template = "carceropolis/publicacao/publicacao_detail.html"
    publicacoes = Publicacao.objects.published().select_related()
    publicacao = get_object_or_404(publicacoes, slug=slug)
    related_posts = publicacao.related_posts.published()
    context = {"publicacao": publicacao, "editable_obj": publicacao,
               "related_posts": related_posts}
    context.update(extra_context or {})
    templates = [template]
    return TemplateResponse(request, templates, context)


def publicacao_feed(request, fmt, **kwargs):
    """Blog posts feeds - maps format to the correct feed view."""
    try:
        return {"rss": PostsRSS, "atom": PostsAtom}[fmt](**kwargs)(request)
    except KeyError:
        raise Http404()

def especialistas_list(request, area_de_atuacao=None, especialidade=None):
    """Display a list of blog posts that are filtered by tag, year, month,
    author or categoria. Custom templates are checked for using the name
    ``carceropolis/publicacao/publicacao_list_XXX.html`` where ``XXX`` is
    either the categoria slug or author's username if given.
    """
    templates = []
    context = {}
    especialistas = Especialista.objects.all()
    especialistas = especialistas.order_by('nome')
    if area_de_atuacao is not None:
        area_de_atuacao = get_object_or_404(AreaDeAtuacao, slug=area_de_atuacao)
        especialistas = especialistas.filter(area_de_atuacao__nome__in=[area_de_atuacao])
        # templates.append(u"carceropolis/especialistas/area_atuacao.html")
        context['area_de_atuacao'] = area_de_atuacao
    if especialidade is not None:
        especialidade = get_object_or_404(Especialidade, slug=especialidade)
        especialistas = especialistas.filter(especialidades__nome__in=[especialidade])
        # templates.append(u"carceropolis/especialistas/especialidade.html")
        context['especialidade'] = especialidade

    prefetch = ("area_de_atuacao", 'especialidades')
    especialistas = especialistas.prefetch_related(*prefetch)
    # especialistas = paginate(especialistas, request.GET.get("page", 1),
                             # settings.PUBLICACAO_PER_PAGE,
                             # settings.MAX_PAGING_LINKS)
    areas_de_atuacao = AreaDeAtuacao.objects.all()
    areas_de_atuacao = areas_de_atuacao.order_by('ordem')
    agrupados = []
    for area in areas_de_atuacao:
        item = {'area': area, 'especialistas':
                especialistas.filter(area_de_atuacao=area)}
        if item['especialistas']:
            agrupados.append(item)
    context = {"especialistas_agrupados": agrupados}
    templates.append(u'carceropolis/especialistas/especialistas.html')
    return TemplateResponse(request, templates, context)

def dados_home(request):
    """Display the Dados Home page, which is a matrix with all available
    categories (only categories, not the items from the Publicação Class).
    """
    templates = ["carceropolis/dados/dados.html"]
    context = {}

    return TemplateResponse(request, templates, context)


def dados_perfil_populacional(request):
    """First test"""
    templates = [u'carceropolis/dados/perfil_populacional.html']
    context = {}

    return TemplateResponse(request, templates, context)


def dados_educacao(request):
    """Second test"""
    templates = [u'carceropolis/dados/educacao.html']
    context = {}

    return TemplateResponse(request, templates, context)


def dados_piramide_etaria(request):
    """Third test"""
    templates = [u'carceropolis/dados/piramide_etaria.html']
    context = {}

    return TemplateResponse(request, templates, context)

def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
        else:
            error(request, "Usuário e/ou senha inválidos.")
    return redirect(next_url(request) or request.META['HTTP_REFERER'])


def register_user(request):
    print("registrando um novo usuário")
    profile_form = get_profile_form()
    form = profile_form(request.POST or None, request.FILES or None)
    print(form)
    print(dir(form))
    print(form.is_valid())
    if request.method == "POST" and form.is_valid():
        print("Método post e form válido")
        new_user = form.save()
        if not new_user.is_active:
            if settings.ACCOUNTS_APPROVAL_REQUIRED:
                print('Usuário cadastrado, aguardando aprovação')
                send_approve_mail(request, new_user)
                info(request, "Obrigado por se cadastrar! Você receberá um "
                              "email quando sua conta for ativada.")
            else:
                print('Usuário cadastrado, aguardando confirmação')
                send_verification_mail(request, new_user, "signup_verify")
                info(request, "Um email de verificação foi enviado com um "
                              "link para ativação de sua conta.")
            return redirect(next_url(request) or "/")
        else:
            print('usuário cadastrado com sucesso')
            info(request, "Cadastro realizado com sucesso")
            login(request, new_user)
            return login_redirect(request)
    else:
        error(request, form)
        return redirect(request.META['HTTP_REFERER']+"#cadastro", kwargs={'registration_form': form})
    return redirect(next_url(request) or request.META['HTTP_REFERER'])


def password_recovery(request):
    # TODO
    pass


def data_dashboard(request, template="dashboard/dashboard.html"):
    """
    Data dashboard.
    """
    script = autoload_server(url='http://localhost:5006/bkapp')
    if request.GET.urlencode():
        state = base64.urlsafe_b64encode(request.GET.urlencode().encode()).decode('utf8')
        mark = 'bokeh-absolute-url'
        insert = 'state=' + state + '&' + mark
        script = script.replace(mark, insert)
    context = {"script": script}
    # context = {"script": ' '.join(script.splitlines()).replace('/script', 'end-script')}
    templates = [template]

    return TemplateResponse(request, templates, context)
