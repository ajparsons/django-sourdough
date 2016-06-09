'''
Created on 26 Mar 2016

@author: alex
'''
import codecs
import os
from markdown import markdown

from django.utils.safestring import mark_safe

class MarkDownView(object):
    """
    allows for a basic view where a markdown files is read in and rendered
    
    Give the class a markdown_loc variable which is the filepath to the markdown files.
    
    use self.get_markdown() to retrieve markdown text. If using clean, it is avaliable as 
    'markdown' in the templpate.
    
    """
    markdown_loc = ""
    
    def get_markdown(self):
        f = codecs.open(self.__class__.markdown_loc, "rb", "cp1252")
        txt = f.read()
        md = mark_safe(markdown(txt))
        return md
    
    def view(self,request):
        return {"markdown":self.get_markdown()}
    
    
