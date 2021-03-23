from django.core.management import BaseCommand
from importlib import import_module
from django.apps import apps as project_apps


class Command(BaseCommand):
    """
    Example usage:

    manage.py populate
    manage.py populate appname

    Looks for an app/populate.py and runs
    a populate function

    an argument specified after --option is
    passed through as a position argument

    """
    help = "Enter an app to populate"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*', type=str)
        parser.add_argument('--option', nargs=1, default="", type=str)

    def handle(self, *args, **options):
        apps = options['app']
        extra_options = [x for x in [options['option']] if x]
        if len(apps) == 0:
            apps = [x.name for x in project_apps.get_app_configs()]
        for app in apps:
            try:
                app = import_module(app + ".populate")
            except ImportError:
                continue

            if callable(app.populate):
                app.populate(*extra_options)
