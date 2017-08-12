from datetime import date, timedelta
from freela.models import Freelancer, Freela
from celery import task
from emailtools.utils import retorno_vaga, email_sender

@task
def send_seven_days_email():
    date_last_week = date.today() - timedelta(weeks=1)
    freelancers = Freelancer.objects.filter(data_inscrito__gt=date_last_week)
    if len(freelancers) > 0:
        for f in freelancers:
            job = f.job
            nome_pessoa = f.nome
            email = f.email

            email_empresa, email_pessoa = retorno_vaga(empresa=job.empresa,
                        nome_candidato = nome_pessoa,
                        vaga = job.titulo_do_job)

            email_sender(to_email=email,
            subject = "Feedback sobre a oportunidade: {}".format(job.titulo_do_job),
            content = email_pessoa
            )

            email_sender(to_email=job.email_responsavel_empresa,
            subject = "Feedback sobre a oportunidade: {}".format(job.titulo_do_job),
            content = email_empresa
            )
