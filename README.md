[![Maintainability](https://api.codeclimate.com/v1/badges/86f23287eac22e4885bd/maintainability)](https://codeclimate.com/github/vmesel/PyJobs/maintainability)

# PyJobs (Antigo pyfreelas)

Repositório do site PyJobs, um sistema de freelances desenvolvido totalmente em Python para Pythonistas.

## Como instalar e contribuir com o site

Para instalar o repositório do PyJobs em seu computador você deve seguir alguns passos listados a seguir:


### Para o setup de desenvolvedor
```
cd PyJobs/
virtualenv pyjobs
source pyjobs/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///$(pwd)/db.sqlite3" # Pode ser qualquer outro banco
export DEBUG=True
export SENDGRID_API_KEY='sua-key-do-sendgrid-aqui'
export SECRET_KEY='sua-secret-key'
python manage.py migrate
```

Para fazer o deploy no Heroku, basta pegar estes mesmos exports e rodar no Heroku
