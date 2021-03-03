test:
	poetry run coverage run manage.py test
	poetry run coverage html
	poetry run isort **/*.py --check-only
	poetry run black . --check

style:
	poetry run isort **/*.py
	poetry run black .

migrate:
	poetry run python manage.py migrate

makemigrations:
	poetry run python manage.py makemigrations

run:
	poetry run python manage.py runserver

comptrans:
	poetry run python manage.py compilemessages

gentrans:
	poetry run python manage.py makemessages -a

collectstaticdocker:
	poetry run python manage.py collectstatic --no-input