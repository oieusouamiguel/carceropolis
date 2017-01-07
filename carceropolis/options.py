# coding= utf-8
"""Arquivo que irá manter um conjunto de 'opções' (choices)."""
from datetime import datetime

CATEGORIAS = (
    (u'SISTEMA', u'FUNCIONAMENTO DO SISTEMA'),
    (u'PERFIL', u'PERFIL POPULACIONAL'),
    (u'POLÍTICA', u'POLÍTICA CRIMINAL'),
    (u'INTERNACIONAL', u'SISTEMAS INTERNACIONAIS'),
    (u'VIOLÊNCIA', u'VIOLÊNCIA INSTITUCIONAL'),
    (u'OUTROS', u'OUTROS'),
)


YEAR_CHOICES = [(r, r) for r in range(1900, datetime.now().year+1)]

MONTH_CHOICES = [('Janeiro', 'Janeiro'), ('Fevereiro', 'Fevereiro'),
                 ('Março', 'Março'), ('Abril', 'Abril'), ('Maio', 'Maio'),
                 ('Junho', 'Junho'), ('Julho', 'Julho'), ('Agosto', 'Agosto'),
                 ('Setembro', 'Setembro'), ('Outubro', 'Outubro'),
                 ('Novembro', 'Novembro'), ('Dezembro', 'Dezembro')]

########################################
# Options related to UNIDADE PRISIONAL #
########################################

# Pergunta 1.1
# - 1.1. Estabelecimento originalmente destinado a pessoa privadas de liberdade
#        do sexo (marcar apenas uma opção)
SEXO_DESTINACAO = (
    (u'Masculino', u'Masculino'),
    (u'Feminino', u'Feminino'),
    (u'Misto', u'Misto')
)

# Pergunta 1.2
# - 1.2. Tipo de estabelecimento - originalmente destinado (marcar apenas uma
#        opção)
TIPO_ESTABELECIMENTO = (
    (u'PROVISÓRIO', u'Estabelecimento destinado ao recolhimento de presos provisórios'),
    (u'FECHADO', u'Estabelecimento destinado ao cumprimento de pena em regime fechado'),
    (u'SEMI', u'Estabelecimento destinado ao cumprimento de pena em regime semiaberto'),
    (u'ABERTO', u'Estabelecimento destinado ao cumprimento de pena em regime aberto ou de limitação de fim de semana'),
    (u'HOSPITALAR', u'Estabelecimento destinado ao cumprimento de pena em regime aberto ou de limitação de fim de semana'),
    (u'RESSOCIALIZACAO', u'Estabelecimento destinado a diversos tipos de regime'),
    (u'TRIAGEM', u'Estabelecimento destinado à realização de exames gerais e criminológico'),
    (u'PATRONATO', u'Patronato')
)


GESTAO_ESTABELECIMENTO = (
    ('Pública', 'Pública'),
    ('PPP', 'Parceria Público-Privada'),
    ('Co-gestão', 'Co-gestão'),
    ('OSs', 'Organizações sem fins lucrativos')
)


DESTINACAO_ORIGINAL = (
    ('PENAL', 'Concebido como estabelecimento penal'),
    ('ADAPTADO', 'Adaptado para estabelecimento penal')
)


S_N_NA = (
    ('SIM', 'Sim'),
    ('NAO', 'Não'),
    ('N/A', 'Não se aplica (estabelecimento masculino)')
)


def current_year():
    """Returns the current year (XXXX)."""
    return datetime.now().year


def current_month():
    """Returns the current month (text)."""
    return MONTH_CHOICES[datetime.now().month - 1]
