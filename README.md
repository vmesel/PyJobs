# PyFreelas

Repositório do site PyFreelas, um sistema de freelances desenvolvido totalmente em Python para Pythonistas.

## Como instalar e contribuir com o site

Para instalar o repositório do PyFreelas em seu computador você deve seguir alguns passos listados a seguir:


### Para o setup de desenvolvedor
```
cd pyfreelas/
virtualenv pyfreelas
source pyfreelas/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite://seubancodedados.sqlite3" # Pode ser qualquer outro banco
export DEBUG=True
export SENDGRID_API_KEY='sua-key-aqui'
```

Para fazer o deploy no Heroku, basta pegar estes mesmos exports e rodar no Heroku
