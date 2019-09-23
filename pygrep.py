#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import unicode_literals

# The idea comes from
# http://bytes.com/topic/python/answers/169012-grep

import re
import os
import codecs

class GrepElement(object):
    def __init__(self,filename,linenumber,s):
        self.filename=filename
        self.linenumber=linenumber
        self.s=s
        self.string=s.string
        self.matched=s.string[s.start():s.end()]
    def __str__(self):
        a=[]
        a.append("{0} : {1}".format(self.filename,self.linenumber))
        a.append(self.string.replace(self.matched,"\033[0;34;40m"+self.matched+"\033[0;47;40m"))
        return "\n".join(a)
    def __unicode__(self):
        return self.__str__().encode("utf8")

def grep(pattern,files,first_result=False):
    """
    If `first_result` is True, stop the search after the first found result and return a list
    with only one element.
    """
    search = re.compile(pattern).search
    l=[]
    for f in files:
        a=codecs.open(f,"r",encoding="utf8")
        for index, line in enumerate(codecs.open(f,"r",encoding="utf8")):
            s=search(line)
            if s:
                l.append(GrepElement(f,index+1,s))
                if first_result :
                    return l
    return l

