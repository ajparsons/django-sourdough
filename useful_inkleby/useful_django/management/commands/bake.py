from __future__ import absolute_import

from importlib import import_module
import os

from dirsync import sync

from django.core.management import BaseCommand
from django.conf import settings
from django.apps import apps as project_apps
from ...views import AppUrl

class Command(BaseCommand):
    
    help = "Enter an app to bake, or no app label to bake all apps"
    
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*', type=str,default=[])

    
    def handle(self, *args, **options):
        apps = options['app']
        kwargs = [x for x in apps if "=" in x]
        apps = [x for x in apps if x not in kwargs]
        kwargs = [x.split("=") for x in kwargs]
        kwargs = {x:y for x,y in kwargs}
        
        if len(apps) == 0:
            apps = [x.name for x in project_apps.get_app_configs()]
        for app in apps:
            manager = None
            try:
                bake_module = import_module(app +".bake")  
            except ImportError:
                bake_module = None
                
            try:
                views_module = import_module(app +".views")  
            except ImportError:
                views_module = None                
            #run custom bake command
            if bake_module:
                if hasattr(bake_module,"bake"):
                    bake_module.bake()
                    continue
                
            if views_module:
                if bake_module and hasattr(bake_module,"BakeManager"):
                    manager = bake_module.BakeManager(views_module)
                else:
                    manager = BaseBakeManager(views_module)
            if manager:
                manager.bake(**kwargs)

class BaseBakeManager(object):
    
    def __init__(self,views_module=None):
        if views_module:
            self.app_urls = AppUrl(views_module)
        else:
            self.app_urls = None
    
    def create_bake_dir(self):
        if not os.path.exists(settings.BAKE_LOCATION):
            os.makedirs(settings.BAKE_LOCATION)
    
    def copy_static_files(self):
        for d in [settings.STATIC_ROOT]:
            dir_loc = os.path.join(settings.BAKE_LOCATION,"static")
            print "syncing {0}".format(d)
            if os.path.isdir(dir_loc) == False:
                os.makedirs(dir_loc)
            sync(d,dir_loc,"sync")        
        
    def amend_settings(self,**kwargs):
        for k,v in kwargs.iteritems():
            if v.lower() == "true":
                rv = True
            elif v.lower() == "false":
                rv = False
            else:
                rv = v
            setattr(settings,k,rv)

    def bake_app(self):
        self.app_urls.bake()
        
    def bake(self,**kwargs):
        if self.app_urls and self.app_urls.has_bakeable_views():
            self.amend_settings(**kwargs)
            self.create_bake_dir()
            self.copy_static_files()
            self.bake_app()