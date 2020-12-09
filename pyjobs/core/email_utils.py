from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.template import Context

try:
    CURRENT_DOMAIN = Site.objects.get_current().domain
except:
    CURRENT_DOMAIN = "pyjobs.com.br"


def get_email_with_template(template_name, context_specific, subject, to_emails):
    context = {
        "dono_do_site": settings.WEBSITE_OWNER_NAME,
        "nome_do_site": settings.WEBSITE_NAME,
        "url_do_site": settings.WEBSITE_HOME_URL,
        "vaga": context_specific.get("vaga", None),
        "pessoa": context_specific.get("pessoa", None),
        "mensagem": context_specific.get("mensagem", None),
        "job_application": context_specific.get("job_application", None),
    }

    if context["vaga"]:
        context["vaga_close_url"] = context["vaga"].get_close_url()
        context["vaga_listing_url"] = context["vaga"].get_listing_url()

    plain_text = get_template(f"{CURRENT_DOMAIN}/emails/{template_name}.txt")
    html_text = get_template(f"{CURRENT_DOMAIN}/emails/html/{template_name}.html")

    text_content, html_content = plain_text.render(context), html_text.render(context)

    msg = EmailMultiAlternatives(
        subject, text_content, settings.WEBSITE_GENERAL_EMAIL, to_emails
    )
    msg.attach_alternative(html_content, "text/html")

    return msg
