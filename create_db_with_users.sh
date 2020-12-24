#!/bin/bash
# assumes migration folder is emty and db file does not exist already

. venv/Scripts/activate
python manage.py delete_db_and_migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser2 --username admin --password admin --noinput --email 'admin@admin.com'
python manage.py createuser2 --username test_user --password houseplants
python manage.py create_plants
python manage.py add_user_plants --count 10 --username 'test_user'
python manage.py add_user_propagations --count 10 --username 'test_user'
exit