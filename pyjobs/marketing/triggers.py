from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from raven.contrib.django.raven_compat.models import client


from pyjobs.marketing.newsletter import subscribe_user_to_mailer
from pyjobs.marketing.models import Messages
from pyjobs.core.models import Job, JobApplication, Profile
from pyjobs.marketing.utils import post_telegram_channel
from pyjobs.core.email_utils import get_email_with_template


@receiver(post_save, sender=Profile)
def add_user_to_mailchimp(sender, instance, created, **kwargs):
    if instance.on_mailing_list:
        subscribe_user_to_mailer(instance)


@receiver(post_save, sender=JobApplication)
def send_email_notifing_job_application(sender, instance, created, **kwargs):
    if not created:
        return

    person_email_context = {
        "vaga": instance.job,
        "pessoa": instance.user.profile,
        "mensagem": instance,
    }

    company_email_context = person_email_context

    template_person = "job_application_registered"
    person_email_subject = "Parabéns! Você se inscreveu na vaga!"
    person_to_send_to = [instance.user.email]

    if instance.job.is_challenging:
        template_person = "job_interest_challenge"
        person_email_subject = "Teste Técnico da empresa: {}!".format(
            instance.job.company_name
        )
        instance.email_sent = True
        instance.email_sent_at = datetime.now()
        instance.save()

    msg_email_person = get_email_with_template(
        template_person, person_email_context, person_email_subject, person_to_send_to
    )
    msg_email_person.send()

    if instance.job.receive_emails:
        msg_email_company = get_email_with_template(
            "job_applicant",
            company_email_context,
            "Você possui mais um candidato para a sua vaga",
            [instance.job.company_email],
        )
        msg_email_company.send()


def send_offer_email_template(job):
    message = Messages.objects.filter(message_type="offer").first()
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        settings.WEBSITE_OWNER_EMAIL,
        [job.company_email, "viniciuscarqueijo@gmail.com"],
    )


def send_feedback_collection_email(job):
    message = Messages.objects.filter(message_type="feedback")[0]
    message_text = message.message_content.format(company=job.company_name)
    message_title = message.message_title.format(title=job.title)
    send_mail(
        message_title,
        message_text,
        settings.WEBSITE_OWNER_EMAIL,
        [job.company_email, settings.WEBSITE_OWNER_EMAIL],
    )


@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    if not created:
        return

    # post to telegram
    message_base = "Nova oportunidade! {} - {} em {}\n {}/job/{}/"
    message_text = message_base.format(
        instance.title,
        instance.company_name,
        instance.workplace,
        settings.WEBSITE_HOME_URL,
        instance.pk,
    )
    post_telegram_channel(message_text)

    msg = get_email_with_template(
        "published_job",
        {"vaga": instance},
        "Sua oportunidade está disponível no {}".format(settings.WEBSITE_NAME),
        [instance.company_email],
    )
    msg.send()
    try:
        send_offer_email_template(instance)
    except:
        client.captureException()
