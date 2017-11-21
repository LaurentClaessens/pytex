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

# copyright (c) Laurent Claessens, 2010-2017
# email: laurent@claessens-donadello.eu

import sys
import codecs
import re

LOGGING_FILENAME=".pytex.log"

# If one moves the class 'ReferenceNotFoundException', one has to update the message in pytex.
class ReferenceNotFoundException(Exception):
    """
    Exception raised when pytex is not able to find back the fautive \\ref causing a future reference.

    EXPLANATION

    In order to detect the future references, pytex creates a big latex document (in RAM) that recursively contains all the \input. This is more or less a single self-contained file equivalent to the given file.

    When a future reference is found in that document, we search back the line in the real files in order to provide the user an instructive message (filename+line number)

    Suppose that we have
    \input{foo}     % this is a comment
    and that the last line of 'foo.tex' contains the fautive \\ref :
    "using theorem \ref{LAB}, blah"

    In that case, the processus of creating the big document will replace the  \input{foo} by its content and LEAVE THE COMMENT, so that we are left with the line

    "using theorem \ref{LAB}, blah    % this is a comment"           (1)

    (in fact the comment itself is discarded but this is an other story : the point is that we get extra spaces and %)

    So when searching back the line, we are searching for the line (1) which does not exist in the actual code.


    HOW TO FIX MY CODE ?

    you should do one or more of the following
    - add an empty (or not empty) line after the line containing the fautive \\ref
    - remove the comment on the line containing the \input.
    
    """
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return self.text

def ensure_unicode(s):
    """
    Return a 'unicode' object that represents 's'. 
    No conversion if 's' is already unicode.

    str->unicode (via s.decode("utf8"))
    unicode->unicode (identity map)
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


def dprint(*args):
    """
    This function is for debug purpose. It serves to roughly print stuff
    on the screen. Then "grep dprint" helps to remove all the garbage.
    """
    a=[str(x) for x in list(args)]
    print(" ".join(a))

def logging(text,pspict=None):
    import codecs
    #text=ensure_unicode(text)
    if pspict :
        text="in "+pspict.name+" : "+text
    print(text)
    with codecs.open(LOGGING_FILENAME,"a",encoding="utf8") as f:
        f.write(text+"\n")

def ensure_unicode(text):
    """
    No more useful since python3
    """
    return text

def testtype(s):
    print(s,type(s))

def RemoveComments(text):
    """
    Takes text as a tex source file and remove the comments including what stands after \end{document}
    Input : string
    Output : string
    """
    line_withoutPC = []
    # we remove the end of lines with % if not preceded by \
    pattern = "[^\\\]%"
    search=re.compile(pattern).search
    # This search only matches the % that are preceded by something else than \.
    # This does not match the % at the beginning of the line. This is why a second test is performed.
    for lineC in text.split("\n"):
        s=search(lineC)

        if s :
            ligne=s.string[:s.start()+2]    # We keep the "%" itself.
        else :             
            ligne=lineC

        # % at the beginning of a line is not matched by the regex.
        if ligne.startswith("%"):
            ligne="%"

        line_withoutPC.append(ligne)
    code_withoutPC = "\n".join(line_withoutPC)

    # Now we remove what is after \end{document}

    final_code=code_withoutPC
    if "\end{document}" in code_withoutPC :
        final_code = code_withoutPC.split("\end{document}")[0]+"\end{document}"
    return final_code

