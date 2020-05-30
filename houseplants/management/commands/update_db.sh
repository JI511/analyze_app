#!/bin/bash
# checkout specific repos or update if already exists

cd ../../../

python manage.py remove_model_items
python manage.py makemigrations houseplants
python manage.py migrate houseplants
python manage.py populate_db ~/Desktop/Programs/analyze_django/mysite/analyze_app/media/Houseplant_Images/

# will need support to activate Python virtual env