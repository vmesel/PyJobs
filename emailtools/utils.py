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
