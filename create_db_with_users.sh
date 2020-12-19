#!/bin/bash
# assumes migration folder is emty and db file does not exist already

. venv/Scripts/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser2 --username admin --password admin --noinput --email 'admin@admin.com'
python manage.py createuser2 --username test_user --password houseplants
exit