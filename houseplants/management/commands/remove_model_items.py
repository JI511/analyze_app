from django.core.management.base import BaseCommand
from . import _model_util as mdl_util


class Command(BaseCommand):
    """
    Base class for creating command.
    """

    def handle(self, *args, **options):
        """
        Calls what is relevant
        """
        mdl_util.remove_items()
