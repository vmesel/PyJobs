import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

def email_sender(to_email, subject, content, from_email="pyfreelas@pyfreelas.com.br"):
    from_email = Email(from_email)
    to_email = Email(to_email)
    subject = subject
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

def empresa_cadastrou_vaga(empresa, vaga):
        return """
Olá {empresa},

Seja bem vindo(a) ao PyFreelas, a plataforma que lhe ajudará a encontrar a pessoa que é necessária em sua equipe!

Agora que você criou a vaga {vaga}, nós lhe enviaremos os detalhes de quem se inscreveu para ela, assim você conseguirá entrar em contato com eles

Em breve, nós lhe contataremos com as pessoas que se inscreveram para a sua vaga!

Abraços,
Vinicius Mesel
@vmesel
""".format(empresa=empresa, vaga=vaga)

def contato_prospect(tipo, nome):
    if tipo:
        return """
Olá pessoal da {nome},

Tudo bem com vocês?

Eu sou Vinícius Mesel, e atualmente eu tenho trabalhado em um website chamado PyFreelas, um site que pretendemos preencher com o máximo de vagas que contenham Python em todo o Brasil.

Eu gostaria de saber se você tem interesse que eu anuncie suas vagas de desenvolvedores Python no PyFreelas, assim poderemos alcançar todos os programadores Python do Brasil.

O PyFreelas é uma plataforma que trabalha para que todos da comunidade Python consigam atingir seus objetivos profissionais.

O link para o PyFreelas é: http://www.pyfreelas.com.br

Se vocês prefererirem, vocês mesmos podem cadastrar uma oportunidade no PyFreelas entrando no site e clicando em “cadastrar oportunidade”. Também gostaria de seu sincero feedback sobre o site e como eu posso ajudar vocês na escolha de profissionais.

Abraços,
Vinicius Mesel
Founder do PyFreelas""".format(nome=nome)
    return """
Olá {nome},

Tudo bem com você?

Eu sou Vinícius Mesel, e atualmente eu tenho trabalhado em um website chamado PyFreelas, um site que pretendemos preencher com o máximo de vagas que contenham Python em todo o Brasil.

Eu gostaria de saber se você tem interesse que eu anuncie suas vagas de desenvolvedores Python no PyFreelas, assim poderemos alcançar todos os programadores Python do Brasil.

O PyFreelas é uma plataforma que trabalha para que todos da comunidade Python consigam atingir seus objetivos profissionais.

O link para o PyFreelas é: http://www.pyfreelas.com.br

Se você prefererir, você podem cadastrar uma oportunidade no PyFreelas entrando no site e clicando em “cadastrar oportunidade”. Também gostaria de seu sincero feedback sobre o site e como eu posso ajudar você na escolha de profissionais.

Abraços,
Vinicius Mesel
Founder do PyFreelas""".format(nome=nome)


def contato_cadastrado(nome="", email="", portfolio="", vaga="", empresa=False):
    if not empresa:
        return """
Olá {nome},

Seja bem vindo(a) ao PyFreelas, a plataforma que lhe ajudará a encontrar a melhor oportunidade para você!

Recebemos seu interesse na oportunidade: {vaga}

Estamos lhe enviando este email para te avisar que a empresa responsável pela sua vaga recebeu seus dados e em breve, eles entrarão em contato com você!

Em breve, nós lhe contataremos com mais informações sobre a vaga!

Abraços,
Vinicius Mesel
@vmesel
""".format(nome=nome, vaga=vaga)
    else:
        return """
Olá,

Você recebeu uma nova pessoa interessada em sua vaga: {vaga}

Nome do interessado(a): {nome}
Email do interessado(a): {email}
Portfolio do interessado(a): {portfolio}

Estamos lhe enviando este email para te avisar que a pessoa está interessada em sua vaga e aguarda uma resposta!

Em breve, nós lhe contataremos com mais interessados!

Abraços,
Vinicius Mesel
@vmesel
""".format(nome=nome, vaga=vaga, email=email, portfolio=portfolio)

def retorno_vaga(empresa, nome_candidato, vaga, tipo_empresa):
        return ("""
Olá pessoal da {nome_empresa},

Tudo bem com vocês?

Nós do PyFreelas gostariamos de saber como foi a conversa com o candidato {nome_candidato} para a oportunidade: {vaga}

Para dar o feedback para nós, preencha o formulário através deste link: https://docs.google.com/forms/d/16Jr7ZkjtAtvncT73x1_hmLdi1JC9olBUCsiOpY201no/viewform

Abraços,
PyFreelas
""".format(empresa=empresa, nome_candidato=nome_candidato, vaga=vaga),
"""
Olá {nome_candidato},

Tudo bem com vocês?

Nós do PyFreelas gostariamos de saber como foi a conversa para a oportunidade: {vaga}

Para dar o feedback para nós, preencha o formulário através deste link: https://docs.google.com/forms/d/e/1FAIpQLScpuibIeqHlC34cm8OzPjvvvt_sN5pKV1GTfJ-OBXDatPADQA/viewform

Abraços,
PyFreelas
""".format(empresa=empresa, nome_candidato=nome_candidato, vaga=vaga))
