from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from raven.contrib.django.raven_compat.models import client


from pyjobs.marketing.newsletter import subscribe_user_to_mailer
from pyjobs.marketing.models import Messages, PushMessage
from pyjobs.core.models import Job, JobApplication, Profile
from pyjobs.marketing.utils import post_telegram_channel
from pyjobs.core.email_utils import get_email_with_template

from github import Github

from webpush import send_group_notification
from django.utils.translation import gettext_lazy as _


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
    person_email_subject = _("Parabéns! Você se inscreveu na vaga!")
    person_to_send_to = [instance.user.email]

    if instance.job.is_challenging:
        template_person = "job_interest_challenge"
        person_email_subject = " ".join(
            map(str, [_("Teste Técnico da empresa: "), instance.job.company_name, "!"])
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
            str(_("Você possui mais um candidato para a sua vaga")),
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
        [job.company_email],
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


def send_job_to_github_issues(job):
    g = Github(settings.GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(settings.GITHUB_DEFAULT_REPO)
    issue_draft = Messages.objects.filter(message_type="github").first()
    issue_title = issue_draft.message_title.format(
        title=job.title, company_name=job.company_name, workplace=job.workplace
    )

    issue_content = issue_draft.message_content.format(
        description=job.description,
        requirements=job.requirements,
        workplace=job.workplace,
        state=job.get_state_display(),
        labels="\n - ".join([skill.name for skill in job.skills.all()]),
        contract_form=job.get_contract_form_display(),
        job_id=job.id,
        website_url=settings.WEBSITE_HOME_URL,
    )
    issue = repo.create_issue(issue_title, issue_content)
    job.issue_number = issue.id
    job.save()


@receiver(post_save, sender=Job)
def new_job_was_created(sender, instance, created, **kwargs):
    if not created or not instance.receive_emails:
        return

    # post to telegram
    message_text = " ".join(
        map(
            str,
            [
                _("Nova oportunidade!"),
                instance.title,
                " - ",
                instance.company_name,
                _("em"),
                instance.workplace,
                "\n",
                f"{settings.WEBSITE_HOME_URL}/job/{instance.pk}/",
            ],
        )
    )
    post_telegram_channel(message_text)

    msg = get_email_with_template(
        "published_job",
        {"vaga": instance},
        " ".join(
            map(str, [_("Sua oportunidade está disponível no"), settings.WEBSITE_NAME])
        ),
        [instance.company_email],
    )

    payload = {
        "head": " ".join(map(str, [_("Nova Vaga!"), instance.title])),
        "body": instance.description,
        "url": f"{settings.WEBSITE_HOME_URL}/job/{instance.pk}/",
    }

    msg.send()
    if not instance.issue_number:
        try:
            send_job_to_github_issues(instance)
        except:
            pass

    try:
        send_group_notification(group_name="general", payload=payload, ttl=1000)
    except:
        pass

    try:
        send_offer_email_template(instance)
    except:
        client.captureException()


@receiver(pre_save, sender=JobApplication)
def feedback_was_created(sender, instance, **kwargs):
    if not instance.id:
        return

    original_application = JobApplication.objects.get(id=instance.id)

    if original_application.company_feedback != instance.company_feedback:
        msg = get_email_with_template(
            "job_application_feedback",
            {
                "pessoa": instance.user,
                "vaga": instance.job,
                "job_application": instance,
            },
            " ".join(
                map(
                    str,
                    [
                        _("Você recebeu um feedback da vaga"),
                        instance.job.title,
                        _("na empresa"),
                        instance.job.company_name,
                    ],
                )
            ),
            [instance.user.email],
        )
        msg.send()


@receiver(post_save, sender=PushMessage)
def send_push_message(sender, instance, **kwargs):
    if not instance.id:
        return

    payload = {
        "head": instance.head,
        "body": instance.body,
        "url": instance.url,
    }
    send_group_notification(group_name="general", payload=payload, ttl=1000)
