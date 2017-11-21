# -*- coding: utf8 -*-

###########################################################################
#   This is the package latexparser
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# copyright (c) Laurent Claessens, 2010,2012-2016
# email: laurent@claessens-donadello.eu

import re

def ensure_unicode(text):
    """
    No more useful since python3
    """
    return text

def testtype(s):
    print(s,type(s))

def dprint(*s):
    print(s)

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

