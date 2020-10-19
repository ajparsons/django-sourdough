from __future__ import absolute_import

from importlib import import_module
import os

from dirsync import sync

from django.core.management import BaseCommand
from django.conf import settings
from django.apps import apps as project_apps
from ...views import AppUrl
from ...views.bake import BaseBakeManager


class Command(BaseCommand):
    """
    example usage:

    manage.py bake
    manage.py bake appname

    When it examines an app will look for:

    A bake.py with a bake function
    A views module with a BakeManager subclassed from BaseBakeManager
    A views module using views subclassed from BakeView
    """
    help = "Enter an app to bake, or no app label to bake all apps"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs='*', type=str, default=[])

        parser.add_argument(
            '--only_absent',
            action='store_true',
            help='Only create absent files',
        )

        parser.add_argument(
            '--only_views',
            nargs="*",
            default=[],
            type=str,
            help='restrict to this view name only',
        )

        parser.add_argument(
            '--only_old',
            nargs="?",
            default=0,
            type=int,
            help='Only replace old files',
        )

        parser.add_argument(
            '--retry_errors',
            nargs="?",
            default=3,
            type=int,
            help='Number of times to retry pages with an error (default 3)',
        )

        parser.add_argument(
            '--skip_static',
            action='store_true',
            help='Skip the static sync',
        )

        parser.add_argument(
            '--skip_errors',
            action='store_true',
            help='Skip files that cause errors',
        )

        parser.add_argument(
            '--skip_assets',
            action='store_true',
            help='Do not render and store charts or other assets',
        )

        parser.add_argument(
            '--all_assets',
            action='store_true',
            help='Rerender existing charts or assets',
        )

        parser.add_argument(
            '--worker',
            default=0,
            type=int,
            help='Which worker this is, divides queues into sections',
        )

        parser.add_argument(
            '--worker_count',
            default=4,
            type=int,
            help='Number of workers (ignored if no worker param)',
        )

        for n in range(1,11):
            parser.add_argument(
                '--restrict_{0}'.format(n),
                default=None,
                type=str,
                help='Restrict arg {0} to value'.format(n),
            )

    def handle(self, *args, **options):
        apps = [x for x in options['app'] if x not in kwargs]

        if len(apps) == 0:
            apps = [x.name for x in project_apps.get_app_configs()]
        for app in apps:
            manager = None
            try:
                bake_module = import_module(app + ".bake")
            except ImportError:
                bake_module = None

            try:
                views_module = import_module(app + ".views")
            except ImportError:
                views_module = None
            # run custom bake command
            if bake_module:
                if hasattr(bake_module, "bake"):
                    bake_module.bake()
                    continue

            if views_module:
                if bake_module and hasattr(bake_module, "BakeManager"):
                    manager = bake_module.BakeManager(views_module)
                else:
                    manager = BaseBakeManager(views_module)
            if manager:
                manager.bake(options)
