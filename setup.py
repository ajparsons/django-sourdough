from distutils.core import setup
setup(
  name = 'useful_inkleby',
  packages = ['useful_inkleby',
              'useful_inkleby.files',
              'useful_inkleby.useful_django',
              'useful_inkleby.useful_django.fields',
              'useful_inkleby.useful_django.models',
              'useful_inkleby.useful_django.views',
              ],
  version = '0.2',
  description = 'A set of django and generic tools',
  author = 'Alex Parsons',
  author_email = 'alex@alexparsons.co.uk',
  url = 'https://github.com/ajparsons/useful_inkleby', 
  download_url = 'https://github.com/ajparsons/useful_inkleby/0.2', 
  keywords = ['django'], 
  classifiers = [],
)