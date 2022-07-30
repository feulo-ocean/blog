Para deploy no Heroku

FAzer login

## cria app
heroku create <nome do app>
## cria Banco
heroku addons:create heroku-postgresql:hobby-dev --app <nome do app>
## ve config do app
heroku config --app blog-python-ocean