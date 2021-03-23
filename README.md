# django-sourdough

Tools for fast population and baking to static files of data exploration sites. 

Forked and reduced version of `useful_inkleby` package - docs there are useful for moment: http://useful-inkleby.readthedocs.io/en/latest/

Python 3 and django 2+ only.

Management commands:

`python manage.py populate` - looks for a populate.populate function in either all apps, or apps listed after populate. 
`python manage.py bake` - renders to a static site any compatible apps (or a specific app listed)

Bake command command line switches:


* --only_views 'view.url.name', 'second.view.name' - only bake certain views. 
* --only_absent - only render pages that haven't already been rendered. 
* --only_old [1] - number of days old a file needs to be to be regenerated
* --skip_errors - proceed over all errors (errors can be reviewed in `bake_dir\error_log.txt`)
* --retry_errors - number of times to retry, default is 3
* --skip_static - do not copy static files to bake directory
* --worker_count - how many workers are working at the same time
* --worker - which worker this is 
* --restrict_1 - restrict the first argument returned from 'bake_args' to this value. Lets you only re-render certain ranges.
* --restrict_2 - etc
* --skip_assets - hook for asset generation like charts - turns off
* --all_assets - hook for asset generation like charts - re-render all
* --verbose_level - setting this to '1' takes out the file by file path prints. (default 2)

Populate command line switches:

* --option : specify a one word option to pass as an arg to the populate function in an app.