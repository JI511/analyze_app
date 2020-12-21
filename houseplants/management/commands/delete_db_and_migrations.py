import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        db_path = os.path.join(os.getcwd(), 'db.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Removed db.sqlite3 file")
        migrations_folder = os.path.join(os.getcwd(), 'houseplants', 'migrations')
        for migration in os.listdir(migrations_folder):
            if migration != '__init__.py' and migration.endswith('.py'):
                os.remove(os.path.join(migrations_folder, migration))
                print("Removed %s in migrations folder" % migration)
