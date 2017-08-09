import sendgrid
import os
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

def email_sender(to_email, subject, content):
    from_email = Email("pyfreelas@pyfreelas.com.br")
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
