import sendgrid
import os

def empresa_cadastrou_vaga(empresa, vaga):
        return """
Olá {empresa},

Agora que você criou a vaga {vaga}, nós lhe enviaremos os detalhes de quem se inscreveu para ela, assim você conseguirá entrar em contato com eles

Em breve, nós lhe contataremos com as pessoas que se inscreveram para a sua vaga!

Abraços,
Vinicius Mesel
@vmesel
""".format(empresa=empresa, vaga=vaga)

def contato_cadastrado(pessoa, vaga, empresa=False):
    if not empresa:
        return """
Olá {nome},

Recebemos seu interesse na oportunidade: {vaga}

Estamos lhe enviando este email para te avisar que a empresa responsável pela sua vaga recebeu seus dados e em breve, eles entrarão em contato com você!

Em breve, nós lhe contataremos com mais informações sobre a vaga!

Abraços,
Vinicius Mesel
@vmesel
""".format(nome=pessoa.get_full_name(), vaga=vaga)
    else:
        return """
Olá,

Você recebeu uma nova pessoa interessada em sua vaga: {vaga}

Nome do interessado(a): {nome}
Email do interessado(a): {email}
Telefone do interessado(a): {telefone}
Linkedin do interessado(a): {linkedin}
GitHub do interessado(a): {github}
Portfolio do interessado(a): {portfolio}
Skills do interessado(a): {skills}

Estamos lhe enviando este email para te avisar que a pessoa está interessada em sua vaga e aguarda uma resposta!

Em breve, nós lhe contataremos com mais interessados!

Abraços,
Vinicius Mesel
@vmesel
""".format(
    nome=pessoa.get_full_name(),
    vaga=vaga,
    email=pessoa.email,
    telefone=pessoa.profile.telefone,
    portfolio=pessoa.profile.portfolio,
    github=pessoa.profile.github,
    linkedin=pessoa.profile.linkedin,
    skills=", ".join([skill.skill for skill in pessoa.profile.skills.get_queryset()])
)

def user_cadastrado(pessoa):
        return """
Olá {nome},

Seja bem vindo ao PyJobs, a plataforma que vai te ajudar a encontrar a vaga perfeita ou a pessoa que você precisa para sua empresa!

Estamos lhe enviando este email para te avisar que você já pode desfrutar de nosso site!

Abraços,
Vinicius Mesel
@vmesel
""".format(nome=pessoa.get_full_name())
