# PyJobs - O Site de Vagas Python Open Source
[![Chatroom](https://img.shields.io/badge/chat-Telegram-blue.svg)](https://t.me/joinchat/Cc8X5A-re7F8F4AIP0lSeg)
[![Build Status](https://img.shields.io/travis/vmesel/PyJobs/master.svg)](https://travis-ci.org/vmesel/PyJobs)
[![Maintainability](https://img.shields.io/codeclimate/maintainability-percentage/vmesel/PyJobs.svg)](https://codeclimate.com/github/vmesel/PyJobs/maintainability)
[![Test Coverage](https://img.shields.io/codeclimate/coverage/vmesel/PyJobs.svg)](https://codeclimate.com/github/vmesel/PyJobs/test_coverage)

O PyJobs é o site de job listing de vagas Python no Brasil, nele você consegue se cadastrar para diversas vagas de emprego e de freelas que podem aparecer no país. Você pode contribuir com código ou ainda com valores monetários no: [Apoia-Se](https://apoia.se/pyjobs)

### Clonar o repositório
```
git clone https://github.com/vmesel/PyJobs.git
cd PyJobs/
cp .env-sample .env
```

Para você poder subir a sua versão do PyJobs, crie um `.env` dentro da pasta PyJobs contendo as seguintes informações:

### Dependências

1. [Instalar docker](https://docs.docker.com/install/)
2. [Instalar o docker-compose](https://docs.docker.com/compose/install/)

### Para utilizar o Docker com o Docker Compose:

```
docker-compose build
docker-compose run web python manage.py migrate
docker-compose up
```

#### Testes

```
docker-compose run --rm web make test
```

### Possíveis dificuldades com o desenvolvimento do PyJobs

#### Utilizar o formulário de cadastro de vaga para cadastrar uma vaga:

Ao tentar utilizar o formulário sem configurar os dados do RECAPTCHA o servidor do Django retorna um erro 500, não permitindo a inserção da vaga no sistema. Configure o recaptcha no seu computador local utilizando este [tutorial](https://stackoverflow.com/questions/46421887/how-to-use-recaptcha-v2-on-localhost?rq=1).

#### Erro ao enviar algum e-mail.

Possivelmente, se você tiver exportado a variável de ambiente do SENDGRID com as API keys inválidas, você muito provavelmente terá algum erro. Para evitar isso, utilize o backend padrão do Django para envios de e-mails, assim eles aparecerão no terminal.
