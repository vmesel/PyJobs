import json
from pprint import pprint
from django.conf import settings

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyjobs.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from apps.core.models import Company, Profile
from apps.jobs.models import Job
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
f = open("jobs.json")

data = json.load(f)

for i in data[2:]:
    data_to_insert = i["fields"]
    try:
        user_created = User.objects.create_user(
            username=data_to_insert["email_responsavel_empresa"],
            email=data_to_insert["email_responsavel_empresa"],
            first_name=data_to_insert["empresa"],
            password="senha1234"
        )
    except IntegrityError:
        user_created = User.objects.get(username = data_to_insert["email_responsavel_empresa"])

    try:
        company_created = Company.objects.create(
            usuario=user_created,
            nome=data_to_insert["empresa"],
            email=data_to_insert["email_responsavel_empresa"],
            site=data_to_insert["link_da_empresa"],
            descricao="Descreva sua empresa em algumas palavras"
        )
    except:
        company_created = Company.objects.get(usuario = user_created)

    job_created = Job.objects.create(
        titulo_do_job=data_to_insert["titulo_do_job"],
        empresa=company_created,
        descricao=data_to_insert["descricao"],
        requisitos=data_to_insert["requisitos"],
        local=data_to_insert["local"],
        publico=True
    )
    # break
