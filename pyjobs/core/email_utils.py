from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def empresa_cadastrou_vaga(empresa, vaga):
    return """
Olá {empresa},

Agora que você criou a vaga {vaga}, nós lhe enviaremos os detalhes de quem se inscreveu para ela, assim você conseguirá\
 entrar em contato com eles

Em breve iremos lhe enviar o link da sua vaga para divulgação!

Abraços,
{dono_do_site}
""".format(
        empresa=empresa, vaga=vaga, dono_do_site=settings.WEBSITE_OWNER_NAME
    )


def vaga_publicada(job):
    return """
Olá {empresa},

Agora a vaga {vaga} foi avaliada por nossos colaboradores e foi publicada!

Para acessar a sua vaga, entre no link:
{url_do_site}/job/{pk}/

Caso você queira fechar essa vaga, utilize esse link secreto que só você tem:
{url_do_site}{close_url}

ATENÇÃO: este link fecha a vaga sem necessidade de confirmação ou senha! Caso haja algum problema,
Por favor, nos contate!


Abraços,
Vinicius Mesel
@vmesel
""".format(
        empresa=job.company_name,
        vaga=job.title,
        pk=job.pk,
        close_url=job.get_close_url(),
        url_do_site=settings.WEBSITE_HOME_URL,
    )


def contato_cadastrado_empresa(pessoa, vaga):
    return """
    Olá,

    Você recebeu uma nova pessoa interessada em sua vaga: {vaga}

    Nome do interessado(a): {nome}
    Email do interessado(a): {email}
    Telefone do interessado(a): {telefone}
    Linkedin do interessado(a): {linkedin}
    GitHub do interessado(a): {github}
    Portfolio do interessado(a): {portfolio}

    Estamos lhe enviando este email para te avisar que a pessoa está interessada em sua vaga e aguarda uma resposta!

    Em breve, nós lhe contataremos com mais interessados!

    Para acessar o {nome_do_site}, entre no link: {url_do_site}

    Abraços,
    {dono_do_site}
    """.format(
        nome=pessoa.get_full_name(),
        vaga=vaga,
        email=pessoa.email,
        telefone=pessoa.profile.cellphone,
        portfolio=pessoa.profile.portfolio,
        github=pessoa.profile.github,
        linkedin=pessoa.profile.linkedin,
        url_do_site=settings.WEBSITE_HOME_URL,
        nome_do_site=settings.WEBSITE_NAME,
        dono_do_site=settings.WEBSITE_OWNER_NAME,
    )


def contato_cadastrado_pessoa(pessoa, vaga):
    return """
Olá {nome},

Recebemos seu interesse na oportunidade: {vaga}

Estamos lhe enviando este email para te avisar que a empresa responsável pela sua vaga recebeu seus dados e em breve,\
 eles entrarão em contato com você!

Em breve, nós lhe contataremos com mais informações sobre a vaga!

Para acessar o {nome_do_site}, entre no link: {url_do_site}

Abraços,
{dono_do_site}
""".format(
        nome=pessoa.get_full_name(),
        vaga=vaga,
        url_do_site=settings.WEBSITE_HOME_URL,
        nome_do_site=settings.WEBSITE_NAME,
        dono_do_site=settings.WEBSITE_OWNER_NAME,
    )


def contact_email(name, email, subject, message):
    return """
Olá,

A pessoa: {name} quer falar sobre {subject}.

A mensagem dela é:

{message}

Para mandar um email para ela, basta enviar para: {email}
    """.format(
        name=name, email=email, subject=subject, message=message
    )


def get_email_with_template(template_name, context_specific, subject, to_emails):
    context = {
        "dono_do_site": settings.WEBSITE_OWNER_NAME,
        "nome_do_site": settings.WEBSITE_NAME,
        "url_do_site": settings.WEBSITE_HOME_URL,
        "vaga": context_specific.get("vaga", None),
        "pessoa": context_specific.get("pessoa", None),
        "mensagem": context_specific.get("mensagem", None),
    }
    plain_text = get_template("emails/{}.txt".format(template_name))
    html_text = get_template("emails/html/{}.html".format(template_name))

    text_content, html_content = plain_text.render(context), html_text.render(context)

    msg = EmailMultiAlternatives(
        subject, text_content, settings.WEBSITE_GENERAL_EMAIL, to_emails
    )
    msg.attach_alternative(html_content, "text/html")

    return msg
