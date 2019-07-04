def empresa_cadastrou_vaga(empresa, vaga):
    return """
Olá {empresa},

Agora que você criou a vaga {vaga}, nós lhe enviaremos os detalhes de quem se inscreveu para ela, assim você conseguirá\
 entrar em contato com eles

Em breve iremos lhe enviar o link da sua vaga para divulgação!

Abraços,
Vinicius Mesel
@vmesel
""".format(
        empresa=empresa, vaga=vaga
    )


def vaga_publicada(job):
    return """
Olá {empresa},

Agora a vaga {vaga} foi avaliada por nossos colaboradores e foi publicada!

Para acessar a sua vaga, entre no link:
http://www.pyjobs.com.br/job/{pk}/

Caso você queira fechar essa vaga, utilize esse link secreto que só você tem:
http://www.pyjobs.com.br{close_url}

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

    Para acessar o PyJobs, entre no link: http://www.pyjobs.com.br

    Abraços,
    Vinicius Mesel
    @vmesel
    """.format(
        nome=pessoa.get_full_name(),
        vaga=vaga,
        email=pessoa.email,
        telefone=pessoa.profile.cellphone,
        portfolio=pessoa.profile.portfolio,
        github=pessoa.profile.github,
        linkedin=pessoa.profile.linkedin,
    )


def contato_cadastrado_pessoa(pessoa, vaga):
    return """
Olá {nome},

Recebemos seu interesse na oportunidade: {vaga}

Estamos lhe enviando este email para te avisar que a empresa responsável pela sua vaga recebeu seus dados e em breve,\
 eles entrarão em contato com você!

Em breve, nós lhe contataremos com mais informações sobre a vaga!

Para acessar o PyJobs, entre no link: http://www.pyjobs.com.br

Abraços,
Vinicius Mesel
@vmesel
""".format(
        nome=pessoa.get_full_name(), vaga=vaga
    )


def contact_email(name, email, subject, message):
    return """
Olá PyJobs,

A pessoa: {name} quer falar sobre {subject}.

A mensagem dela é:

{message}

Para mandar um email para ela, basta enviar para: {email}
    """.format(
        name=name, email=email, subject=subject, message=message
    )
