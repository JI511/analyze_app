#!/bin/bash
# checkout specific repos or update if already exists

cd ../../../

python manage.py remove_model_items
python manage.py makemigrations houseplants
python manage.py migrate houseplants
# The argument is the directory where the wanted media files reside.
python manage.py populate_db $1

# will need support to activate Python virtual env? All this really needs is Django support but you never know
# what the host computer may have.