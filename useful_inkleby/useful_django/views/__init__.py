from functional import *
from bake import *
from url import *
from social import *
from exceptions import *

class ComboView(BakeView,SocialView,IntegratedURLView):
    pass