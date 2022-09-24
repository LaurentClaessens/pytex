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

# copyright (c) Laurent Claessens, 2010,2012-2017, 2019-2020
# email: laurent@claessens-donadello.eu

import os.path
import codecs
from pytex.src.log_code import LogCode
from pytex.src.LatexCode import LatexCode

def FileToLatexCode(name,fast=False,keep_comments=False):
    """ return a codeLaTeX from a file """
    content = FileToText(name)
    A = LatexCode(content,filename=name,keep_comments=keep_comments)
    A.included_file_list=[name]
    return A

def FileToText(name):
    """ return the content of a file as string

    If the file do not exist, return empty string.
    """
    l=[]
    if not os.path.isfile(name):
        return ""
    for line in codecs.open(name,"r",encoding="utf8"):
        l.append(line)
    return "".join(l)

def string_to_latex_code(s):
    return LatexCode(s)

def FileToLogCode(options, stop_on_first=False):
    """ return a codeLog from a file """
    name = options.log_filename
    try:
        list_content = list(codecs.open(name,"r",encoding="utf8"))
    # I've noticed that the log file was ISO-8859 English text
    except UnicodeDecodeError :
        print("Problem with",name)
        list_content = list(codecs.open(name,"r",encoding="iso8859-1"))
    a="".join(list_content)
    return LogCode("".join(list_content),
                   options=options,
                   filename=name,
                   stop_on_first=stop_on_first)


def list_of_citations(filelist):
    """
    Return the list of arguments in \cite{...}.

    From a list of files, return the list of arguments in \cite{...}.
    """
    citations = []
    new_filelist = [a+".tex" for a in filelist]
    for new_file in new_filelist:
        code_latex = FileToLatexCode(new_file)
        occurrences = code_latex.analyse_use_of_macro(r"\cite", 1)
        for occ in occurrences:
            citations.append(occ.label)
    return citations
