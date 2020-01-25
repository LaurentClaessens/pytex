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

# copyright (c) Laurent Claessens, 2010,2012-2016, 2020
# email: laurent@claessens-donadello.eu

"""
This module furnishes some functionalities to manipulate LaTeX code.
"""

import os
import re
import codecs

definition_commands = [ "\\newcommand","\\renewcommand" ]   # In the method dict_of_definition_macros, I hard-code the fact that 
                                # these definition commands have 3 arguments.
def FileToCodeBibtex(name):
    """ return a codeBibtex from a file """
    content = FileToText(name)
    return CodeBibtex(content,filename=name)

def MacroDefinition(code,name):
    r"""
    Finds the (last) definition of a macro and returns the corresponding object

    text : the text (a LaTeX source file) where we are searching in
    name : the name of the macro we want to analyse

    We search for the definition under one of the two forms
    \newcommand{\name}[n]{definitio}
    \newcommand{\name}{definitio}

    I'm not sure of the behaviour if the macro is not found in the text. (update me)
    """
    if type(code) == LatexCode :
        return code.dict_of_definition_macros()[name]
    else :
        print("Warning: something is wrong. I'm not supposed to be here. Please contact the developer")
        return LatexCode(code).dict_of_definition_macros()[name]

class StatisticsOfTheMacro(object):
    def __init__(self,code,name):
        if type(code) != LatexCode :
            code = LatexCode(code)
        self.name = name
        self.definition = MacroDefinition(code,name)
        self.occurrences = SearchUseOfMacro(code,name)
        self.number_of_use = len(self.occurrences)

class newlabelNotFound(object):
    """Exception class for LatexCode.get_newlabel_value"""
    def __init__(self,label_name):
        self.label_name = label_name

def CreateBibtexFile(big_bibtex_file,small_bibtex_file,list_of_files):
    r"""
    Put in small_bibtex_file the bibex code needed for all the citations in list_of_files. Take the bibtex code from big_bibtex_file

    An error is raised if
    - a citation has no code in big_bibtex_file         (it is raised in CodeBibtex.extract_list)
    - the code is already in small_bibtex_file, but is different to the one in big_bibtex_file

    A warning is written if 
    - an entry in small_bibtex_file is not used in the list_of_files.
    """
    citations = list_of_citations(list_of_files)
    big_bibtex=FileToCodeBibtex(big_bibtex_file)
    extracted_big=big_bibtex.extract_list(citations)
    small_bibtex=FileToCodeBibtex(small_bibtex_file)
    for label in small_bibtex.entry_dict.keys() :
        if label not in citations:
            print("Useless entry : %s"%label)
    new_bibtex=extracted_big+small_bibtex
    new_bibtex.save(small_bibtex_file)

class AddBibtexError(Exception):
    def __init__(self,text):
        self.text=text

def EntryListToCodeBibtex(l):
    """From a list of object of type BibtexEntrym create the corresponding CodeBibtex"""
    text = "\n".join( [a.given_text for a in l] )
    return CodeBibtex(text)

class BibtexEntry(object):
    """
    Contain the informations about a bibtex entry.

    self.type is the type of document (book,article,...). It is returned in lowercase.
    self.labe is the label.
    """
    def __init__(self,given_text):
        self.given_text=given_text
        at_position=self.given_text.find("@")
        open_bracket_position=self.given_text.find("{")
        comma_position=self.given_text.find(",")
        self.type = self.given_text[at_position+1:open_bracket_position].lower()
        self.label = self.given_text[open_bracket_position+1:comma_position].replace(" ","")

class CodeBibtex(object):
    """
    Contain informations about a bibtex file

    Many assumptions are made on the code.
    1. The character @ appearing at the beginning of a line is always the beginning of an entry
    2. The lines are beginning by
    @TYPE{LABEL
    with no space between @ and TYPE neither between { and the label.
    """
    def __init__(self,given_text,filename=None):
        self.filename=filename
        self.given_text="\n"+given_text         # Border effect because I search for entries by matching the string "\n@"
        self.text_brut = ConvertToUTF8(RemoveComments(self.given_text))
        split_entry_list=self.text_brut.split("\n@")
        self.entry_list=[ BibtexEntry("@"+text) for text in split_entry_list[1:] ]
        dico={}
        for entry in self.entry_list :
            dico[entry.label]=entry
        self.entry_dict=dico
    def extract_list(self,label_list):
        """
        From a list of labels, return the code of a bibtex file containing only these

        The exit value is a new object of type CodeBibtex.
        """
        a=[]
        for label in label_list:
            try :
                a.append(self.entry_dict[label].given_text)
            except KeyError:
                print("I have no entry labelled %s"%label)
                raise
        return CodeBibtex("\n".join(a))
    def save(self,filename=None):
        """Save the code in a file"""
        f = codecs.open(filename,"w","utf_8")
        f.write(self.given_text)
        f.close()
    def __getitem__(self,key):
        return self.entry_dict[key]
    def __add__(self,other):
        """
        Add two CodeBibtex in the following way.

        If A and B are two object of type CodeBibtex, return a new object whose entry_list is the union of the two. 
        If there are intersections, analyse the content of the entry (given_text) and if the contents are not equal, raise an exception.
        """
        dico=self.entry_dict
        for entry in other.entry_dict.values():
            if entry.label in dico :
                if other[entry.label].given_text != self[entry.label].given_text:
                    raise NameError("Different texts for the label %s"%entry.label)
            dico[entry.label]=entry
        return EntryListToCodeBibtex(dico.values())
