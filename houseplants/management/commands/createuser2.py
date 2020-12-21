import django.contrib.auth
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', help='The name of the user.')
        parser.add_argument('--password', help='The name of the user.')

    def handle(self, *args, **options):
        user_model = django.contrib.auth.get_user_model()
        user = user_model.objects.create_user(options['username'], password=options['password'])
        user.is_superuser = False
        user.is_staff = False
        user.save()
        print("User %s created successfully" % options['username'])
