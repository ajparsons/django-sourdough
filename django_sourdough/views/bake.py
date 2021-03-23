
import datetime
import io
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from dirsync import sync
from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.http import HttpResponse
from django.test.client import RequestFactory
from django.urls import reverse

from .functional import LogicalView
from .url import AppUrl

try:
    from htmlmin.minify import html_minify
except Exception:
    def html_minify(x): return x

import six

if six.PY2:
    from inspect import getargspec
else:
    from inspect import signature


def bake_static():
    """
    syncs the static file location to the bake directory
    """
    for d in settings.STATICFILES_DIRS:
        print("syncing {0}".format(d))
        sync(d, os.path.join(settings.BAKE_LOCATION, "static"), "sync")


class BakeView(LogicalView):
    """

    Extends functional view with baking functions.

    expects a bake_args() generator that returns a series
    of different sets of arguments to bake into files.

    expects a BAKE_LOCATION - in django settings

    render_to_file() - render all possible versions of this view.

    """

    bake_path = ""
    bake_file_type = "html"
    baking_options = {"baking": False}

    def add_to_error_log(self,
                         bake_location,
                         path,
                         error,
                         error_log="error_log.txt"):
        """
        Record errors path with basic information on cause.
        """
        cls_name = self.__class__.__name__
        d = datetime.now().isoformat()
        e_name = type(error).__name__
        line = f"{d}: {cls_name} : {path} : {e_name} {error}\n"

        with open(Path(bake_location, error_log), 'a') as f:
            f.write(line)

    @classmethod
    def bake(cls, **kwargs):
        """
        render all versions of this view into a files
        """
        class_name = cls.url_name
        verbose_level = kwargs["verbose_level"]
        print("baking {type}".format(type=class_name))
        cls.baking_options.update(kwargs)
        cls.baking_options["baking"] = True
        cls._prepare_bake()
        i = cls()

        func = i.bake_args
        limit_query = None
        if six.PY2:
            arg_no = len(getargspec(i.bake_args).args)
        else:
            arg_no = len(signature(i.bake_args).parameters)

        if arg_no > 1:
            generator = i.bake_args(limit_query)
        else:
            generator = i.bake_args()

        options = list(generator)

        if options:
            # based on --restrict_1, restrict_2 arguments
            # reduce arguments just to those that match
            for n in range(1, 11):
                restrict = kwargs["restrict_{0}".format(n)]
                if restrict:
                    options = [
                        x for x in options if not x or x[n-1] in restrict]

        total_to_bake = float(len(options))

        # can split the task into different piles for different workers
        worker_count = kwargs["worker_count"]
        worker = kwargs["worker"]
        if worker:
            print("Processing as worker {0} of {1}".format(
                worker, worker_count))
            worker_threshold = worker
            if worker == worker_count:
                worker_threshold = 0
        step = 20
        start = datetime.now()
        process_count = 0
        alert_template = "{type}: {done} out of {total} ({percent}%) {time}"
        for n, o in enumerate(options):
            # divide work into piles and skip those not needed
            if worker:
                if (n + 1) % worker_count != worker_threshold:
                    continue
            process_count += 1
            if o is None:
                rendered = i.render_to_file(**kwargs)
            else:
                rendered = i.render_to_file(o, **kwargs)
            if process_count % step == 0 and rendered and verbose_level > 0:
                end = datetime.now()
                time_taken = end - start
                p = round(((n+1)/total_to_bake) * 100, 2)
                print(alert_template.format(type=class_name,
                                            done=n+1,
                                            total=total_to_bake,
                                            percent=p,
                                            time=end.isoformat()))
                print("{step} completed in {time}.".format(
                    step=step, time=time_taken))
                start = end

    @ classmethod
    def _prepare_bake(self):
        """
        class method - store modifications for the class for class
         - e.g. precache many objects for faster render
        """

        pass

    def _get_bake_path(self, *args):
        """
        override to have a more clever way of specifying
        the destination to write to
        uses class.bake_path is present, if not constructs
        from url of view
        """
        if self.__class__.bake_path:
            if args:
                bake_path = self.__class__.bake_path.format(*args)
            else:
                bake_path = self.__class__.bake_path
        else:
            rev = reverse(self.__class__.url_name, args=args)[1:]
            parts = rev.split("/")
            bake_path = os.path.join(*parts)
            extension = "." + self.__class__.bake_file_type
            if bake_path[-len(extension):] == extension:
                extension = ""
            if bake_path[-1] in ["/", "\\"]:
                bake_path += "index" + extension
            else:
                bake_path += extension

        return os.path.join(settings.BAKE_LOCATION,
                            bake_path)

    def render_to_file(self,
                       args=None,
                       only_absent=False,
                       only_old=0,
                       skip_errors=False,
                       retry_errors=3,
                       verbose_level=2,
                       **kwargs):
        """
        renders this set of arguments to a files
        """
        if args is None:
            args = []

        file_path = self._get_bake_path(*args)

        if only_absent and os.path.isfile(file_path):
            return False

        if os.path.isfile(file_path) and only_old:
            t = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(t)
            if last_modified > datetime.now() - timedelta(days=only_old):
                return False

        if verbose_level > 1:
            print(u"saving {0}".format(file_path))
        directory = os.path.dirname(file_path)
        if os.path.isdir(directory) is False:
            os.makedirs(directory)

        request_path = file_path.replace(settings.BAKE_LOCATION, "")
        request_path = request_path.replace(
            "\\", "/").replace("index.html", "").replace(".html", "")
        request = RequestFactory().get(request_path)

        error_count = 0
        context = None
        # error handling, allow repeats or skip
        while context is None:
            try:
                context = self._get_view_context(request, *args)
            except Exception as e:
                error_count += 1
                if error_count < retry_errors:
                    print("retrying {0}".format(error_count))
                    time.sleep(5)
                    pass
                else:
                    self.add_to_error_log(settings.BAKE_LOCATION,
                                          request_path,
                                          e
                                          )
                    if not skip_errors:
                        raise e
                    else:
                        error_notice = "suppressing error: {0} - {1}"
                        e_name = type(e).__name__
                        print(
                            error_notice.format(e_name, e))
                        break
        if not context:
            return None

        banned_types = ['text/csv']

        # if a valid response has already been 
        # generated by some layer of the structure

        if isinstance(context, HttpResponse):
            html = html_minify(context.content)
            if context["Content-Type"] not in banned_types:
                html = html.replace(
                    "<html><head></head><body>", "")
                html = html.replace("</body></html>", "")
        else:
            # normal case, we give the context to a view
            error_count = 0
            result = None
            # error handling, allow repeats or skip
            while result is None:
                try:
                    result = self.context_to_html(request, context)
                except Exception as e:
                    error_count += 1
                    if error_count < retry_errors:
                        print("retrying {0}".format(error_count))
                        time.sleep(5)
                        pass
                    else:
                        if not skip_errors:
                            raise e
                        else:
                            e_name = type(e).__name__
                            error_notice = "suppressing error: {0} - {1}"
                            print(
                                error_notice.format(e_name, e))
                            break

            if not result:
                return False

            html = html_minify(result.content)

        if type(html) == bytes:
            with io.open(file_path, "wb") as f:
                f.write(html)
        else:
            with io.open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

        return True

    @ classmethod
    def write_file(cls, args, path, minimise=True):
        """
        more multi-purpose writer - accepts path argument
        """
        request = RequestFactory().get(path)
        content = cls.as_view(decorators=False)(
            request, *args).content
        if b"<html" in content and minimise:
            content = html_minify(content)
        if type(content) == bytes:
            content = str(content, "utf-8", errors="ignore")
        print(u"writing {0}".format(path))
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def bake_args(self, limit_query=None):
        """
        subclass with a generator that feeds
        all possible arguments into the view
        """
        return [None]


class BaseBakeManager(object):
    """
    Manager for bake command function
    Subclass as views.BakeManager to add more custom behaviour

    """

    def __init__(self, views_module=None):
        if views_module:
            self.app_urls = AppUrl(views_module)
        else:
            self.app_urls = None

    def create_bake_dir(self):
        if not os.path.exists(settings.BAKE_LOCATION):
            os.makedirs(settings.BAKE_LOCATION)

    def get_static_destination(self):
        if hasattr(settings, "BAKE_STATIC_LOCATION"):
            return settings.BAKE_STATIC_LOCATION
        else:
            return os.path.join(settings.BAKE_LOCATION, "static")

    def copy_static_files(self):
        for d in [settings.STATIC_ROOT]:
            dir_loc = self.get_static_destination()
            print("syncing {0}".format(d))
            if os.path.isdir(dir_loc) is False:
                os.makedirs(dir_loc)
            sync(d, dir_loc, "sync")

    def amend_settings(self, **kwargs):
        pass

    def bake_app(self):
        self.app_urls.bake(**self.arg_options)

    def bake(self, options):
        """
        this is the main function
        """
        self.arg_options = options
        if self.app_urls and self.app_urls.has_bakeable_views():
            self.amend_settings()
            self.create_bake_dir()
            if options["skip_static"] is False:
                self.copy_static_files()
            self.bake_app()
