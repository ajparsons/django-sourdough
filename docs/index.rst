.. useful_inkleby documentation master file, created by
   sphinx-quickstart on Thu Jun 09 11:28:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

useful_inkleby
==========================================

Contents:

.. toctree::
   :maxdepth: 2

Collection of useful tools for django projects.

useful_django.models:

* FlexiModel - Allows manager and queryset methods to be added to a model using @managermethod and @querysetmethod decorators rather than creating custom managers. 
* EasyBulkModel - Cleaner bulk creation of objects - store objects to be queued with .queue() and then trigger the save with model.save_queue(). Saves objects in batches. Returns completed objects (nicer than bulk_create).
* StockModelHelpers - Generic methods useful to all models.
* FlexiBulkModel - Combines the above into one class. 

useful_django.views:

* IntegratedURLView - Integrates django's url settings directly the view classes rather than keeping them in a separate urls.py.
* BakeView - Handles baking a view into files - expects a function that can feed it arbitrary sets of arguments and a BAKE_LOCATION in the settings. 
* FunctionalView - Slimmed down version of class-based views where functional logic is preserved - but class structure used to tidy up common functions. 
* MarkDownView - Mixin to read a markdown file into the view. 
* ComboView - combines BakeView, IntegratedURLView (most common combo I use). 

useful_django.fields:

* JsonBlockField - simple serialisation field that can be handed arbitrary sets of objects for restoration later. Classes can be registered for cleaner serialisation (if you'd like to be able to modify the raw values while stored for instance). 
   


Indices and tables
==================

* :ref:`genindex`
* modules_	
* :ref:`search`

