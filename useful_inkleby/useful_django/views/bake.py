
from django.core.handlers.base import BaseHandler  
from django.test.client import RequestFactory 


from django.conf import settings

import os
import io
from functional import LogicalView
from dirsync import sync
from django.http import HttpResponse

try:
    from htmlmin.minify import html_minify
except:
    html_minify = lambda x: x

    
def bake_static():
    """
    syncs the static file location to the bake directory
    """
    for d in settings.STATICFILES_DIRS:
        print "syncing {0}".format(d)
        sync(d,os.path.join(settings.BAKE_LOCATION,"static"),"sync")


class RequestMock(RequestFactory):  
    """
    Construct a generic request object to get results of view
    """
    def request(self, **request):
        #https://gist.github.com/tschellenbach/925270
        request = RequestFactory.request(self, **request)  
        handler = BaseHandler()  
        handler.load_middleware()  
        for middleware_method in handler._request_middleware:  
            if middleware_method(request):  
                raise Exception("Couldn't create request mock object - "  
                                "request middleware returned a response")  
        return request 


class BakeView(LogicalView):
    """

    Extends functional view with baking functions. 
    
    expects a bake_args() generator that returns a series
    of different sets of arguments to bake into files.
    
    expects a BAKE_LOCATION - in django settings
    
    render_to_file() - render all possible versions of this view.
    
    """
    
    bake_path = ""

    @classmethod
    def bake(cls,limit_query=None,**kwargs):
        """
        render all versions of this view into a files
        """
        if cls.bake_path:
            print "baking {0}".format(cls.__name__)
            cls._prepare_bake()
            i = cls()
            for o in i.bake_args(limit_query):
                if o == None:
                    i.render_to_file(**kwargs)
                else:
                    i.render_to_file(o,**kwargs)
        else:
            raise ValueError("This view has no location to bake to.")
    
    @classmethod
    def _prepare_bake(self):
        """
        class method - store modifications for the class for class - e.g. precache many objects
        for faster render
        """
        
        pass
    
    def _get_bake_path(self,*args):
        """
        override to have a more clever way of specifying 
        the destination to write to
        """
        if args:
            return os.path.join(settings.BAKE_LOCATION,
                                self.__class__.bake_path.format(*args))
        else:
            return os.path.join(settings.BAKE_LOCATION,
                                self.__class__.bake_path)


    
    def render_to_file(self,args=None,only_absent=False):
        """
        renders this set of arguments to a files
        """
        if args == None:
            args = []

        file_path = self._get_bake_path(*args)
        
        if only_absent and os.path.isfile(file_path):
            return None
        
        print u"saving {0}".format(file_path)
        directory = os.path.dirname(file_path)
        if os.path.isdir(directory) == False:
            os.makedirs(directory)
        
        request = RequestMock().request()
        
        request.path = "/" + file_path.replace(settings.BAKE_LOCATION,"")
        request.path = request.path.replace("\\","/").replace("index.html","").replace(".html","")

        context = self._get_view_context(request,*args)
        if isinstance(context,HttpResponse):
            html = html_minify(context.content).replace("<html><head></head><body>","").replace("</body></html>","")
        else:
            html = html_minify(self.context_to_html(request,context).content)
        
        with io.open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        
    @classmethod
    def write_file(cls,args,path, minimise=True):
        """
        more multi-purpose writer - accepts path argument
        """
        request = RequestMock().request()
        content = cls.as_view(decorators=False,no_auth=True)(request,*args).content
        if "<html" in content and minimise:
            content = html_minify(content)
        if type(content) == str:
            content = unicode(content,"utf-8", errors="ignore")
        print u"writing {0}".format(path)
        with io.open(path,"w",encoding="utf-8") as f:
            f.write(content)

        
    def bake_args(self,limit_query):
        """
        subclass with a generator that feeds all possible arguments into the view
        """
        return [None]