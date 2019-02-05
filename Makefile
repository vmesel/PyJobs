test:
	coverage run manage.py test
	coverage html
	isort **/*.py --check-only
	black . --check
