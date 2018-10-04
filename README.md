[![Build Status](https://circleci.com/gh/vmesel/PyJobs.svg?branch=master)](https://circleci.com/gh/vmesel/PyJobs)
[![codecov](https://codecov.io/gh/ikaromn/PyJobs/branch/master/graph/badge.svg)](https://codecov.io/gh/ikaromn/PyJobs)


# PyJobs - O Site de Vagas Python Open Source


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

Para utilizar o Docker com o Docer Compose:

Rode `docker-compose build` e depois rode `docker-compose up`
