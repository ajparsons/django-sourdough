'''

IntegratedURLView - Sidestep django's url.py based setup and integrate
urls directly with view classes rather than keeping them seperate.

This will mix-in either with the functional inkleby view or the default
django class-based views. 

In views module you set up a series of classes that inherit from
IntegratedURLView and then connect up in project url like so:

url(r'^foo/', include_view('foo.views')),

Philosophy behind this is that the current urlconf system was designed for
functional views - class-based  views have to hide themselves as functions 
with an as_view function, which is ugly. By moving responsibility for 
generating these to the class view it avoids awkward manual repetition 
and keeps all settings associated with the view in one place.
Apps then don't need a separate url.py. 

'''


from django.conf.urls import url
import six
from importlib import import_module
from functional import FunctionalView
from types import ModuleType


class AppUrl(object):

    def __init__(self,app_view):
        """
        
        Given path to views (or views module) will gather all url-enabled views
        """
        self.views = []
        
        if isinstance(app_view,ModuleType):
            view_module = app_view
        elif isinstance(app_view, six.string_types):
            view_module = import_module(app_view)
        else:
            raise TypeError("Not a module or module path")
        
        
        for o in view_module.__dict__.iteritems():
            if hasattr(o[1],"url_pattern"):
                self.views.append(o[1])

    def patterns(self):            
        """
        return patterns of all associated views
        """
    
        local_patterns = []
        for c in self.views:
            local_patterns.extend(c.get_pattern())
            
        local_patterns.sort(key = lambda x:len(x._regex), reverse=True)
        return local_patterns
    
    def bake(self,**kwargs):
        """
        bake all views with a bake_path
        """
        for v in self.views:
            if hasattr(v,"bake_path") and v.bake_path:
                v.bake(**kwargs)

def include_view(app_view):
    return AppUrl(app_view).patterns()

class IntegratedURLView(FunctionalView):
    """
    
    Integrate URL configuration information into the View class.
    
    Makes app level urls.py unnecessary. 
    
    add class level variables for:
    
    url_pattern - regex string
    url_patterns - list of regex strings
    url_name - name for url view (for reverse lookup)
    url_extra_args - any extra arguments to be fed into the url function for this view.
    
    """
    
    url_pattern = ""
    url_patterns = []
    url_name = ""
    url_extra_args = {}
    
    @classmethod
    def get_pattern(cls):
        """
        returns a list of conf.url objects for url patterns that match this object
        """
        new_patterns = []
        def urlformat(pattern):
            return url(pattern,cls.as_view(),cls.url_extra_args,name=cls.url_name)
        
        if cls.url_patterns:
            new_patterns = [urlformat(x) for x in cls.url_patterns]
        if cls.url_pattern:
            new_patterns.append(urlformat(cls.url_pattern))
            
        return new_patterns