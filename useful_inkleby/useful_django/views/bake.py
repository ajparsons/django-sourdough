
import datetime
import io
import os
import time
from datetime import datetime

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
except:
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

    @classmethod
    def bake(cls, **kwargs):
        """
        render all versions of this view into a files
        """
        class_name = cls.url_name
        print("baking {type}".format(type=class_name))
        cls.baking_options.update(kwargs)
        cls.baking_options["baking"] = True
        cls._prepare_bake()
        i = cls()

        func = i.bake_args
        limit_query = None
        if six.PY2:
            l = len(getargspec(i.bake_args).args)
        else:
            l = len(signature(i.bake_args).parameters)

        if l > 1:
            generator = i.bake_args(limit_query)
        else:
            generator = i.bake_args()

        options = list(generator)

        if options:
            # based on --restrict_1, restrict_2 arguments - reduce arguments just to those that match
            for n in range(1, 11):
                restrict = kwargs["restrict_{0}".format(n)]
                if restrict:
                    options = [x for x in options if not x or x[n-1] in restrict]

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

        for n, o in enumerate(options):
            # divide work into piles and skip those not needed
            if worker:
                if (n + 1) % worker_count != worker_threshold:
                    continue

            if o == None:
                rendered = i.render_to_file(**kwargs)
            else:
                rendered = i.render_to_file(o, **kwargs)
            if n % step == 0 and rendered:
                end = datetime.now()
                time_taken = end - start
                p = round(((n+1)/total_to_bake) * 100, 2)
                print("{type}: {done} out of {total} ({percent}%)".format(type=class_name,
                                                                          done=n+1,
                                                                          total=total_to_bake,
                                                                          percent=p))
                print("{step} completed in {time}.".format(step=step, time=time_taken))
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
            rev = reverse(self.__class__.url_name, args=args)
            bake_path = rev.replace("/", "\\")[1:]
            extension = "." + self.__class__.bake_file_type
            if bake_path[-len(extension):] == extension:
                extension = ""
            if bake_path[-1] == "\\":
                bake_path += "index" + extension
            else:
                bake_path += extension

        return os.path.join(settings.BAKE_LOCATION,
                            bake_path)

    def render_to_file(self, args=None, only_absent=False, only_old=0, skip_errors=False, retry_errors=3, **kwargs):
        """
        renders this set of arguments to a files
        """
        if args == None:
            args = []


        file_path = self._get_bake_path(*args)

        if only_absent and os.path.isfile(file_path):
            return False

        if os.path.isfile(file_path) and only_old:
            t = os.path.getmtime(file_path)
            last_modified = datetime.datetime.fromtimestamp(t)
            if last_modified > datetime.datetime.now() - datetime.timedelta(days=only_old):
                return False

        print(u"saving {0}".format(file_path))
        directory = os.path.dirname(file_path)
        if os.path.isdir(directory) == False:
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
                    if not skip_errors:
                        raise e
                    else:
                        print(
                            "suppressing error: {0} - {1}".format(type(e).__name__, e))
                        break
        if not context:
            return None

        banned_types = ['text/csv']

        # if a valid response has already been generated by some layer of the structure
        if isinstance(context, HttpResponse):
            html = html_minify(context.content)
            if context["Content-Type"] not in banned_types:
                html = html.replace(
                    "<html><head></head><body>", "").replace("</body></html>", "")
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
                            print(
                                "suppressing error: {0} - {1}".format(type(e).__name__, e))
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
        subclass with a generator that feeds all possible arguments into the view
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
            if os.path.isdir(dir_loc) == False:
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
