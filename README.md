# PyJobs - O Site de Vagas Python Open Source


### Clonar o repositório
```
git clone https://github.com/vmesel/PyJobs.git
cd PyJobs/

```

Para você poder subir a sua versão do PyJobs, crie um `.env` dentro da pasta PyJobs contendo as seguintes informações:

```
RECAPTCHA_SITE_KEY=
RECAPTCHA_SECRET_KEY=
TELEGRAM_TOKEN=TOKEN_AQUI
TELEGRAM_CHATID=CHATID_AQUI
DEBUG=False
EMAIL_BACKEND=
SENDGRID_API_KEY=
SENDGRID_PASSWORD=
SENDGRID_USERNAME=
SECRET_KEY=
```

### Dependências

1. [Instalar docker](https://docs.docker.com/install/)
2. [Instalar o docker-compose](https://docs.docker.com/compose/install/)


### Para utilizar o Docker com o Docker Compose:

```
docker-compose build
docker-compose run web python manage.py migrate
docker-compose up
```