# coding= utf-8
"""Modelos definidos para o Projeto carcerópolis."""
from cidades.models import Cidade, STATE_CHOICES
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from mezzanine.blog.models import BlogPost
from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
from .options import current_month, current_year, MONTH_CHOICES, YEAR_CHOICES
from .validators import check_filetype


class AreaDeAtuacao(models.Model):
    """Categorias Gerais de classificação de Especialistas e Publicações."""
    nome = models.CharField(max_length=250, unique=True,
                            verbose_name='Nome da área')
    descricao = models.TextField(verbose_name='Descrição')
    ordem = models.IntegerField(unique=True, verbose_name='Ordem')
    slug = AutoSlugField(populate_from='nome', always_update=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = 'Área de Atuação'
        verbose_name_plural = 'Áreas de Atuação'


class Especialidade(models.Model):
    """Definição das Especialidades principais mapeadas no projeto."""
    nome = models.CharField(max_length=80, unique=True,
                            verbose_name='Nome da especialidade')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    slug = AutoSlugField(populate_from='nome',
                         always_update=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'


class Especialista(models.Model):
    """Classe que define os especialistas para o 'Banco de Especialistas'."""
    nome = models.CharField(max_length=250)
    email = models.EmailField()
    telefone = PhoneNumberField(blank=True)
    mini_bio = models.CharField(max_length=250, blank=True)
    instituicao = models.CharField(max_length=250,
                                   verbose_name='Instituição')
    area_de_atuacao = models.ManyToManyField(AreaDeAtuacao,
                                             verbose_name='Área de atuação')
    especialidades = models.ManyToManyField(Especialidade)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = 'Especialista'
        verbose_name_plural = 'Especialistas'


class Publicacao(BlogPost):
    """Publicações relacionadas à temática do site."""
    autoria = models.CharField(max_length=150,
                               verbose_name='Autoria')
    categorias = models.ManyToManyField(AreaDeAtuacao,
                                        verbose_name='Categorias')
    ano_de_publicacao = models.IntegerField(verbose_name='Ano de publicacão',
                                             choices=YEAR_CHOICES,
                                             default=current_year)
    arquivo_publicacao = models.FileField(upload_to='publicacoes/',
                                          verbose_name='Arquivo da publicação')

    class Meta:
        verbose_name = 'Publicação'
        verbose_name_plural = 'Publicações'

    def __unicode__(self):
        return self.title


Publicacao._meta.get_field('title').verbose_name = 'Título'
Publicacao._meta.get_field('publish_date').verbose_name = 'Publicado em'
Publicacao._meta.get_field('content').verbose_name = 'Descrição'
Publicacao._meta.get_field('keywords').verbose_name = 'Tags'
Publicacao._meta.get_field('related_posts').verbose_name = 'Posts Relacionados'
Publicacao._meta.get_field('_meta_title').verbose_name = 'Tílulo'
Publicacao._meta.get_field('description').verbose_name = 'Descrição curta'
Publicacao._meta.get_field('gen_description').verbose_name = 'Gerar descrição'
Publicacao._meta.get_field('allow_comments').default = False


class UnidadePrisional(models.Model):
    """Unidades Prisionais."""
    nome_unidade = models.CharField(max_length=255,
                                    verbose_name='Nome da Unidade')
    sigla_unidade = models.CharField(max_length=10)
    tipo_logradouro = models.CharField(max_length=15)
    nome_logradouro = models.CharField(max_length=255)
    numero = models.IntegerField(blank=True, null=True, verbose_name='Número')
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=255)
    municipio = models.ForeignKey(Cidade, verbose_name='Município')
    uf = models.CharField(max_length=2, choices=STATE_CHOICES)
    cep = models.CharField(max_length=8)
    ddd = models.IntegerField(verbose_name='DDD')
    telefone = models.IntegerField()
    email = models.EmailField()

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = 'Unidade Prisional'
        verbose_name_plural = 'Unidades Prisionais'

    @classmethod
    def _new_from_dict(cls, data):
        """Generate a new 'Unidade Prisional' and return it.

        The 'data' attribute is a dictionary with the necessary fields to
        generate a new Unidade Prisional.
        """

        unidade = UnidadePrisional()
        unidade.nome_unidade = data['nome_unidade']
        unidade.sigla_unidade = data['sigla_unidade']
        unidade.tipo_logradouro = data['tipo_logradouro']
        unidade.nome_logradouro = data['nome_logradouro']
        if isinstance(data['numero'], int):
            unidade.numero = data['numero']
        unidade.complemento = data['complemento']
        unidade.bairro = data['bairro']
        unidade.municipio = Cidade.objects.get(nome=data['municipio'],
                                               estado=data['uf'])
        unidade.uf = data['uf']
        unidade.cep = data['cep']
        unidade.ddd = data['ddd']
        unidade.telefone = data['telefone']
        unidade.email = data['email']
        return unidade

    @classmethod
    def _import_from_csv(cls, data):
        """Populate the DB from CSV data.

        The 'data' attribute must be a list of dictionaries, being each dict
        a representation of one UnidadePrisional.
        You should generate the 'data' attribute using the csv.DictRead method.
        """
        atualizadas = []
        novas = []
        errors = []
        for row in data:
            try:
                unidade = UnidadePrisional.objects.get(
                    nome_unidade=row['nome_unidade'])
                unidade._update_from_dict(row)
                unidade.save()
                atualizadas.append(unidade.nome_unidade)
            except ObjectDoesNotExist:
                try:
                    unidade = UnidadePrisional._new_from_dict(row)
                    unidade.save()
                    novas.append(unidade.nome_unidade)
                except Exception as e:
                    error = {'nome_unidade': row['nome_unidade'],
                             'erro': e,
                             'data': row}
                    errors.append(error)

        msg = 'Resumo da operação:\n'
        if atualizadas:
            msg += '    - '
            msg += '{} unidades foram atualizadas.\n'.format(len(atualizadas))
        if novas:
            msg += '    - '
            msg += '{} unidades foram adicionadas.\n'.format(len(novas))

        if errors:
            msg += 'Ocorreram {} erros de importação:\n'.format(len(errors))
            for error in errors:
                msg += '    - '
                msg += 'Nome da Unidade: {}\n'.format(error['nome_unidade'])
                msg += ' | {}'.format(error['erro'])

        print(msg)

    def __unicode__(self):
        return "%s (%s/%s)" % (self.nome_unidade, self.municipio, self.uf)

    def _update_from_dict(self, data):
        """Update a 'Unidade Prisional' based on its name and return it.

        The 'data' attribute is a dictionary with the necessary fields to
        generate a new Unidade Prisional.
        """

        self.sigla_unidade = data['sigla_unidade']
        self.tipo_logradouro = data['tipo_logradouro']
        self.nome_logradouro = data['nome_logradouro']
        if isinstance(data['numero'], int):
            self.numero = data['numero']
        else:
            self.numero = None
        self.complemento = data['complemento']
        self.bairro = data['bairro']
        self.municipio = Cidade.objects.get(nome=data['municipio'],
                                               estado=data['uf'])
        self.uf = data['uf']
        self.cep = data['cep']
        self.ddd = data['ddd']
        self.telefone = data['telefone']
        self.email = data['email']


class BaseMJ(models.Model):
    """Manage the multiple versions of MJ Infopen raw database."""

    ano = models.IntegerField(choices=YEAR_CHOICES, default=current_year)
    mes = models.CharField(verbose_name='Mês', max_length=40,
                           choices=MONTH_CHOICES, default=current_month)
    arquivo = models.FileField(upload_to='base_bruta_mj/',
                               validators=[check_filetype])
    salvo_em = models.DateTimeField(verbose_name='Salvo em', auto_now_add=True)

    def __unicode__(self):
        return "{}/{}".format(self.mes, self.ano)

    class Meta:
        verbose_name = 'Base bruta MJ'
        verbose_name_plural = 'Bases brutas MJ'
