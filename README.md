# PyJobs - O Site de Vagas Python Open Source
[![chatroom icon](https://patrolavia.github.io/telegram-badge/chat.png)](https://t.me/joinchat/Cc8X5A-re7F8F4AIP0lSeg)

O PyJobs é o site de job listing da comunidade Python Brasil, nele você consegue se cadastrar para diversas vagas de emprego e de freelas que podem aparecer na comunidade. Você pode contribuir com código ou ainda com valores monetários no: [Apoia-Se](https://apoia.se/pyjobs)

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
