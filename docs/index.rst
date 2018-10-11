.. useful_inkleby documentation master file, created by
   sphinx-quickstart on Thu Jun 09 11:28:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

useful_inkleby
==========================================

Collection of useful tools for django projects by `Alex Parsons <http://www.github.com/ajparsons>`_. See code on `Github <https://github.com/ajparsons/useful_inkleby>`_.

:py:mod:`useful_inkleby.useful_django.models`:

* FlexiModel - Allows manager and queryset methods to be added to a model using @managermethod and @querysetmethod decorators rather than creating custom managers. 
* EasyBulkModel - Cleaner bulk creation of objects - store objects to be queued with .queue() and then trigger the save with model.save_queue(). Saves objects in batches. Returns completed objects (nicer than bulk_create).
* StockModelHelpers - Generic methods useful to all models.
* FlexiBulkModel - Combines the above into one class. 

:py:mod:`useful_inkleby.useful_django.views`:

* IntegratedURLView - Integrates django's url settings directly into the view classes rather than keeping them in a separate urls.py.
* FunctionalView - Slimmed down version of class-based views where functional logic is preserved - but class structure used to tidy up common functions. 
* LogicalView - expects a logic function where any values assigned to self are passed to template. Other functions can be run before or after using @prelogic and @postlogic operators. 
* SocialView - Allows liquid templates to be used to specify social share formats in class properties

* BakeView - Handles baking a view into files - expects a bake_args function that can feed it arbitrary sets of arguments and a BAKE_LOCATION in the settings. 
* MarkDownView - Mixin to read a markdown file into the view. 
* LogicalURLView - combines BakeView, IntegratedURLView.
* LogicalSocialView - combines BakeView, IntegratedURLView, SocialView.

:py:mod:`useful_inkleby.useful_django.commands`:

* bake appname - triggers baking an app
* populate appname - runs the populate.py script for an app

:py:mod:`useful_inkleby.useful_django.fields`:

* JsonBlockField - simple serialisation field that can be handed arbitrary sets of objects for restoration later. Classes can be registered for cleaner serialisation (if you'd like to be able to modify the raw values while stored for instance). 

:py:mod:`useful_inkleby.files`:

* QuickGrid - compact function to read in spreadsheet and present readable code that translates between spreadsheet headers and internal values (make population scripts nicer). 
* QuickText - compact text reader and writer. 


:py:mod:`useful_inkleby.decorators`:

* GenericDecorator - Cleans up creation of function decorators. 


FlexiModel Usage
==========================================

.. code-block:: python

   from useful_inkleby.useful_django.models import FlexiModel, querysetmethod, managermethod

    class Foo(FlexiModel):
        
        @querysetmethod
        def bar():
            pass
            
        @managermethod
        def foobar():
            pass
        
    Foo.objects.foobar()
    Foo.objects.all().bar()

EasyBulkModel Usage
==========================================

.. code-block:: python

   from useful_inkleby.useful_django.models import EasyBulkModel

    class Model(EasyBulkModel):
        pass

    for x in range(10000):
        m = Model(foo=x)
        m.queue()
        
    Model.save_queue()

IntegratedURLView Usage
==========================================

Move URL patterns and names into the class to get rid of app level urls.py

For the view:

.. code-block:: python

    class AboutView(IntegratedURLView):
        template = "about.html"
        url_pattern = r'^about'
        url_name = "about_view"
        
        def view(self,request):
            f = "foo"
            return {'f':f}

For project urls.py:

.. code-block:: python

    from useful_inkleby.useful_django.views import include_view
    urlpatterns = [
        url(r'^foo/', include_view('foo.views')), #where foo is the app name
        ]    

        
LogicalView Usage
==========================================

Gets rid of the need for messy supers or the hidden logic 
of the django class views. 

Expects a logic function and everything assigned to self is avaliable in view.

other functions can be run before or after with @prelogic and @postlogic

.. code-block:: python

    class AboutView(LogicalView):
        template = "about.html"
        url_pattern = r'^about'
        url_name = "about_view"
        
		@prelogic
		def run_this_before():
			self.text_to_use = "foo"
		
        def logic(self):
			self.f = self.text_to_use

		
BakeView Usage
==========================================

settings.py:

.. code-block:: python

    BAKE_LOCATION = "??" #root to store baked files

views.py:

.. code-block:: python

    class FeatureView(ComboView):
        """
        Feature display view
        """
        template = "feature.html"
        url_pattern = r'^feature/(.*)'
        url_name = "feature_view"
        bake_path = "feature\\{0}.html"

        def bake_args(self):
            """
            arguments to pass into view - a model ref in this case (so equiv to bakery)
            but can also pass non-model arbitrary stuff through.
            """
            features = Feature.objects.all()
            
            for f in features:
                yield (f.ref,)
        
        def logic(self,ref):
            """
            view that is run with the arguments against the template and saved to bake_path
            """
            self.feature = Feature.objects.get(ref=ref)

			
Add 'useful_inkleby.useful_django' to INSTALLED_APPS to use bake command. 

Then you can use 'manage.py bake appname' to bake app. 

You can finetune this by creating bake.py
			
bake.py (script to execute bake):

.. code-block:: python

    from app.views import FeatureView, bake_static
    
    bake_static()
    FeatureView.bake()
    
If combined with IntegratedURLView by using ComboView you can bake a whole app like so:

.. code-block:: python

    from useful_inkleby.useful_django.views import AppUrl,bake_static
    import app.views as views
    
    bake_static()
    AppUrl(views).bake()
    
    
Contents:

.. toctree::
   :maxdepth: 1
   
   useful_inkleby.useful_django.models
   useful_inkleby.useful_django.views
   useful_inkleby.useful_django.fields
   useful_inkleby.files