import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

def email_sender(to_email, subject, content, from_email = "pyfreelas@pyfreelas.com.br"):
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
