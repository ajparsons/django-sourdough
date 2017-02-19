from django.core.management import BaseCommand
from importlib import import_module
from django.apps import apps as project_apps

class Command(BaseCommand):
    
    help = "Enter an app to bake"
    
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*', type=str)
    

    def handle(self, *args, **options):
        apps = options['app']
        if len(apps) == 0:
            apps = [x.name for x in project_apps.get_app_configs()]
        for app in apps:
            try:
                app = import_module(app +".populate")
            except ImportError:
                continue
            
            app.populate()
            