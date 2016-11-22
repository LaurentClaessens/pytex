# -*- coding: utf8 -*-

###########################################################################
#   This is part of the module phystricks
#
#   phystricks is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   phystricks is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with phystricks.py.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# copyright (c) Laurent Claessens, 2010-2016
# email: laurent@claessens-donadello.eu

def ensure_unicode(s):
    """
    Return a 'unicode' object that represents 's'. 
    No conversion if 's' is already unicode.

    str->unicode (via s.decode("utf8"))
    unicode->unicide (identity map)
    """
    if isinstance(s,str):
        return s.decode("utf8")
    if isinstance(s,unicode):
        return s
    testtype(s)
    raise TypeError("You are trying to convert to unicode the following object "+str(s)+" of type "+str(type(s)))

def ensure_str(s):
    """
    Return a 'str' object that represents 's'. 
    No conversion if 's' is already str.

    unicode->str (via s.encode("utf8"))
    str->str (identity map)
    """
    if isinstance(s,str):
        return s
    if isinstance(s,unicode):
        return s.encode("utf8")
    testtype(s)
    raise TypeError("You are trying to convert to unicode the following object "+str(s)+" of type "+str(type(s)))

def testtype(s):
    print(s,type(s))
    print("\n")

def dprint(*args):
    """
    This function is for debug purpose. It serves to roughly print stuff
    on the screen. Then "grep dprint" helps to remove all the garbage.
    """
    a=[str(x) for x in list(args)]
    print(" ".join(a))

def logging(text,pspict=None):
    LOGGING_FILENAME=".pytex.log"
    import codecs
    #text=ensure_unicode(text)
    if pspict :
        text="in "+pspict.name+" : "+text
    print(text)
    with codecs.open(LOGGING_FILENAME,"a",encoding="utf8") as f:
        f.write(text+"\n")
