# coding= utf-8
"""Modelos definidos para o Projeto carcerópolis."""
import csv
import logging

from cidades.models import Cidade, STATE_CHOICES
from autoslug import AutoSlugField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import lazy
from mezzanine.blog.models import BlogPost

from .options import (DESTINACAO_ORIGINAL, GESTAO_ESTABELECIMENTO,
                      MONTH_CHOICES, S_N_NA, SEXO_DESTINACAO,
                      TIPO_ESTABELECIMENTO, YEAR_CHOICES, current_month,
                      current_year)
from .validators import check_filetype

log = logging.getLogger(__name__)


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
    ddi = models.IntegerField(verbose_name='DDI', blank=True, null=True,
                              default=55)
    ddd = models.IntegerField(verbose_name='DDD', blank=True, null=True)
    telefone = models.IntegerField(verbose_name='Telefone', blank=True,
                                   null=True)
    mini_bio = models.CharField(max_length=600, blank=True)
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
    tipo_logradouro = models.CharField(max_length=20)
    nome_logradouro = models.CharField(max_length=255)
    numero = models.IntegerField(blank=True, null=True, verbose_name='Número')
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=255)
    municipio = models.ForeignKey(Cidade, verbose_name='Município')
    uf = models.CharField(max_length=2, choices=STATE_CHOICES)
    cep = models.CharField(max_length=8)
    ddd = models.IntegerField(verbose_name='DDD', null=True, blank=True)
    telefone = models.IntegerField(null=True, blank=True)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Unidade Prisional'
        verbose_name_plural = 'Unidades Prisionais'

    def __unicode__(self):
        return "%s (%s/%s)" % (self.nome_unidade, self.municipio, self.uf)

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
        else:
            try:
                unidade.numero = int(data['numero'])
            except:
                unidade.numero = None
        unidade.complemento = data['complemento']
        unidade.bairro = data['bairro']
        unidade.municipio = Cidade.objects.get(nome=data['municipio'],
                                               estado=data['uf'])
        unidade.uf = data['uf']
        unidade.cep = data['cep']
        if isinstance(data['ddd'], int):
            unidade.ddd = data['ddd']
        else:
            try:
                unidade.ddd = int(data['ddd'])
            except:
                unidade.ddd = None
        if isinstance(data['telefone'], int):
            unidade.telefone = data['telefone']
        else:
            try:
                unidade.telefone = int(data['telefone'])
            except:
                unidade.telefone = None
        unidade.email = data['email']
        return unidade

    @classmethod
    def _import_from_csv(cls, filename):
        """Populate the DB from CSV data.

        The 'data' attribute must be a list of dictionaries, being each dict
        a representation of one UnidadePrisional.
        You should generate the 'data' attribute using the csv.DictRead method.
        """
        atualizadas = []
        novas = []
        errors = []

        fieldnames = ['remove1', 'nome_unidade', 'sigla_unidade',
                      'tipo_logradouro', 'nome_logradouro', 'numero',
                      'complemento', 'bairro', 'municipio', 'uf', 'cep', 'ddd',
                      'telefone', 'email', 'remove2']
        with open(filename, 'r') as csv_file:
            data = csv.DictReader(csv_file, fieldnames=fieldnames)

            for row in data:
                if row['nome_unidade'] == 'nome_unidade':
                    row = data.next()

                del row['remove1']
                del row['remove2']

                try:
                    unidade = UnidadePrisional.objects.get(
                        nome_unidade=row['nome_unidade'],
                        municipio=Cidade.objects.get(nome=row['municipio'],
                                                     estado=row['uf']))
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
                                 'erro': str(e),
                                 'data': row}
                        errors.append(error)

        msg = 'Resumo da operação:\n'
        if atualizadas:
            msg += '    - '
            msg += '{} unidades foram atualizadas.\n'.format(len(atualizadas))
            log.info('    {}'.format(atualizadas))

        if novas:
            msg += '    - '
            msg += '{} unidades foram adicionadas.\n'.format(len(novas))

        if errors:
            msg += 'Ocorreram {} erros de importação:\n'.format(len(errors))
            for error in errors:
                msg += '    - '
                msg += 'Unidade: {:.30}'.format(error['nome_unidade'])
                msg += ' | {} | {}/{}\n'.format(error['erro'],
                                                error['data']['uf'],
                                                error['data']['municipio'])

        log.info(msg)

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
            try:
                self.numero = int(data['numero'])
            except:
                self.numero = None
        self.complemento = data['complemento']
        self.bairro = data['bairro']
        self.municipio = Cidade.objects.get(nome=data['municipio'],
                                            estado=data['uf'])
        self.uf = data['uf']
        self.cep = data['cep']
        if isinstance(data['ddd'], int):
            self.ddd = data['ddd']
        else:
            try:
                self.ddd = int(data['ddd'])
            except:
                self.ddd = None
        if isinstance(data['telefone'], int):
            self.telefone = data['telefone']
        else:
            try:
                self.telefone = int(data['telefone'])
            except:
                self.telefone = None
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


class GESTAO_ESTABELECIMENTO(models.Model):
    """Tipo de modelo de gestão do estabelecimento."""
    modelo_de_gestao = models.CharField('Modelo de Gestão', max_length=50)
    descricao = models.CharField('Descrição', max_length=255)

    class Meta:
        verbose_name = 'Gestão do estabelecimento'


class SERVICO_EXISTENTE(models.Model):
    """Serviço existente na unidade prisional."""
    servico = models.CharField('Serviço', max_length=50)
    descricao = models.CharField('Descrição', max_length=255)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços existentes'


class REGIMENTO_ESPECIFICO(models.Model):
    """Opções para a pergunta 1.9 sobre regimento específico."""
    opcao = models.CharField('Opção', max_length=50)
    descricao = models.CharField('Descrição', max_length=255)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços existentes'


class DadosInfopen(models.Model):
    """Dados do infopen sobre as unidades prisionais."""
    unidade = models.ForeignKey(UnidadePrisional, verbose_name='Unidade Prisional')
    ano = models.IntegerField('Ano da informação',
                              choices=YEAR_CHOICES, default=current_year)
    #
    destinacao = models.CharField(max_length=10, choices=SEXO_DESTINACAO,
                                  verbose_name='Estabelecimento originalmente destinado a pessoa privada de liberdade do sexo')
    #
    # - 1.2. Tipo de estabelecimento - originalmente destinado (marcar apenas uma opção)
    tipo = models.CharField(max_length=100,
                            choices=TIPO_ESTABELECIMENTO,
                            default=TIPO_ESTABELECIMENTO[0][0],
                            verbose_name='Tipo de estabelecimento - originalmente destinado (marcar apenas uma opção)')
    sub_tipo = models.CharField('Tipo de Estabelecimento', max_length=100,
                                default=None)
    # - 1.2.1. Tipo de estabelecimento
    capacidade = models.IntegerField('Capacidade do Estabelecimento', default=0)
    #
    # - Pergunta 1.3 - Capacidade do estabelecimento
    vagas_provisorios_masc = models.IntegerField('vagas (masc) - presos provisórios', null=True, blank=True)
    vagas_fechado_masc = models.IntegerField('vagas (masc) - regime fechado', null=True, blank=True)
    vagas_semiaberto_masc = models.IntegerField('vagas (masc) - regime semiaberto', null=True, blank=True)
    vagas_aberto_masc = models.IntegerField('vagas (masc) - regime aberto', null=True, blank=True)
    vagas_rdd_masc = models.IntegerField('vagas (masc) - Regime Disciplinar Diferenciado (RDD)', null=True, blank=True)
    vagas_internacao_masc = models.IntegerField('vagas (masc) - Medidas de segurança de internação', null=True, blank=True)
    vagas_outros_masc = models.IntegerField('vagas (masc) - outro(s). Qual(is)?', null=True, blank=True)
    vagas_outros_descricao_masc = models.CharField('Quais outras vagas (masc)?', max_length=100, blank=True)
    #
    vagas_provisorios_fem = models.IntegerField('vagas (fem) - presos provisórios', null=True, blank=True)
    vagas_fechado_fem = models.IntegerField('vagas (fem) - regime fechado', null=True, blank=True)
    vagas_semiaberto_fem = models.IntegerField('vagas (fem) - regime semiaberto', null=True, blank=True)
    vagas_aberto_fem = models.IntegerField('vagas (fem) - regime aberto', null=True, blank=True)
    vagas_rdd_fem = models.IntegerField('vagas (fem) - Regime Disciplinar Diferenciado (RDD)', null=True, blank=True)
    vagas_internacao_fem = models.IntegerField('vagas (fem) - Medidas de segurança de internação', null=True, blank=True)
    vagas_outros_fem = models.IntegerField('vagas (fem) - outro(s)', null=True, blank=True)
    vagas_outros_descricao_fem = models.CharField('Quais outras vagas? (fem)', max_length=100, blank=True)
    #
    celas_nao_aptas = models.IntegerField('Quantidade de celas não aptas', null=True, blank=True)
    vagas_desativadas_masc = models.IntegerField('Vagas desativadas - masculino', null=True, blank=True)
    vagas_desativadas_fem = models.IntegerField('Vagas desativadas - feminino', null=True, blank=True)
    #
    # - 1.4. Gestão do estabelecimento (marcar apenas uma opção)
    gestao_do_estabelecimento = models.ManyToManyField(GESTAO_ESTABELECIMENTO,
                                                       verbose_name='Gestão do estabelecimento (marcar apenas uma opção)')
    #
    # - 1.5. Quais serviços são terceirizados? (marcar mais de uma resposta, se aplicável)
    servicos_tercerizados = models.ManyToManyField(SERVICO_EXISTENTE,
                                                   blank=True,
                                                   verbose_name='Quais serviços são terceirizados? (marcar mais de uma resposta, se aplicável)')
    #
    # - 1.6. Data de inauguração do estabelecimento
    data_inauguracao = models.DateField('Data de Inauguração da Unidade')
    #
    # - 1.7. O estabelecimento foi concebido como estabelecimento penal ou foi construído para outra utilização e foi adaptado?
    destino_original = models.CharField('O estabelecimento foi concebido como estabelecimento penal ou foi construído para outra utilização e foi adaptado?',
                                        choices=DESTINACAO_ORIGINAL,
                                        max_length=100,
                                        help_text='O estabelecimento foi concebido como estabelecimento penal ou foi construído para outra utilização e foi adaptado?')
    #
    # - 1.8. Possui regimento interno?
    possui_regimento = models.BooleanField(default=True,
                                           verbose_name='Possui regimento interno?')
    #
    # - 1.9. O regimento interno é específico para este estabelecimento ou se aplica aos demais estabelecimentos do Estado?
    regimento_especifico = models.ForeignKey(REGIMENTO_ESPECIFICO,
                                             blank=True,
                                             verbose_name='O regimento interno é específico para este estabelecimento ou se aplica aos demais estabelecimentos do Estado?')
    #
    # - 2.1. Há cela adequada/ dormitório para gestantes? (apenas para estabelecimentos com vagas para mulheres)
    cela_gestantes = models.CharField('Há cela adequada/ dormitório para gestantes? (apenas para estabelecimentos com vagas para mulheres)',
                                      choices=S_N_NA,
                                      max_length=100)
    #
    # - 2.1.1. Quantidade de gestantes/ parturientes
    qtd_gestantes = models.IntegerField('Quantidade de gestantes/parturientes')
    #
    # - 2.1.2. Quantidade de lactantes
    qtd_lactantes = models.IntegerField('Quantidade de lactantes')
    #
    # - 2.2. Possui berçário e/ou centro de referência materno-infantil? (apenas para estabelecimentos com vagas para mulheres)
    possui_bercarios = models.CharField('Possui berçário e/ou centro de referência materno-infantil? (apenas para estabelecimentos com vagas para mulheres)',
                                        choices=S_N_NA,
                                        max_length=100)
    # - 2.2.1 - Capacidade de bebês
    qtd_bebes = models.IntegerField('Capacidade de bebês')
    #
    # - 2.3. Possui creche? (apenas para estabelecimentos com vagas para mulheres)
    possui_creche = models.CharField('Possui creche? (apenas para estabelecimentos com vagas para mulheres)',
                                     choices=S_N_NA,
                                     max_length=100)
    # - 2.3.1 - Capacidade de crianças
    qtd_criancas = models.IntegerField('Capacidade de crianças')

    class Meta:
        verbose_name = 'Dados Infopen'
        verbose_name_plural = 'Dados Infopen'
