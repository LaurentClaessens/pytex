# -*- coding: utf8 -*-

###########################################################################
#   This is the package LaTeXparser
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

# copyright (c) Laurent Claessens, 2010
# email: moky.math@gmail.com

"""
This is a very basic LaTeX parser and manipulation intended to be used within phystricks and other of my scripts.
"""

import os
import commands
import re
import codecs

paires = { "{":"}","[":"]","`":"'"}

accepted_between_arguments = ["%","\n"," ","    "] # the last one is a TAB
definition_commands = [ "\\newcommand","\\renewcommand" ]   # In the method dict_of_definition_macros, I hard-code the fact that 
                                # these definition commands have 3 arguments.
def FileToText(name):
    """ return the content of a file """
    l=[]
    for line in open(name,"r"):
        l.append(line)
    return "".join(l)

def FileToCodeLaTeX(name):
    """ return a codeLaTeX from a file """
    content = FileToText(name)
    return CodeLaTeX(content,filename=name)
def FileToCodeBibtex(name):
    """ return a codeBibtex from a file """
    content = FileToText(name)
    return CodeBibtex(content,filename=name)

def FileToCodeLog(name):
    """ return a codeLog from a file """
    list_content = list(open(name,"r"))
    return CodeLog("".join(list_content),filename=name)

class Occurrence(object):
    """
    self.as_written : the code as it appears in the file, including \MyMacro, including the backslash.
    self.position : the position at which this occurrence appears. 
        Example, if we look at the CodeLaTeX

        Hello word, \MyMacro{first} 
        and then \MyMacro{second}

        the first occurrence of \MyMacro has position=12
    """
    def __init__(self,name,arguments,as_written="",position=0):
        self.arguments = arguments
        self.number_of_arguments = len(arguments)
        self.name = name
        self.as_written = as_written
        #self.arguments_list = [ a[0] for a in self.arguments ]
        self.arguments_list = arguments
        self.position = position
    def configuration(self):
        r"""
        Return the way the arguments are separated in as_written.
 
        Example, if we have
        \MyMacro<space>{A}<tab>{B}
        {C},
        we return the list
        ["<space>","tab","\n"]

        The following has to be true:
        self.as_written == self.name+self.configuration()[0]+self.arguments_list[0]+etc.
        """
        l=[]
        a = self.as_written.split(self.name)[1]
        for arg in self.arguments_list:
            split = a.split("{"+arg+"}")
            separator=split[0]
            try:
                a=split[1]
            except IndexError:
                print self.as_written
                raise
            l.append(separator)
        return l
    def change_argument(self,num,func):
        r"""
        Apply the function <func> to the <n>th argument of self. Then return a new object.
        """
        n=num-1     # Internally, the arguments are numbered from 0.
        arguments=self.arguments_list
        configuration=self.configuration()
        arguments[n]=func(arguments[n])
        new_text=self.name
        if len(arguments) != len(configuration):
            print "Error : length of the configuration list has to be the same as the number of arguments"
            raise ValueError
        for i in range(len(arguments)):
            new_text=new_text+configuration[i]+"{"+arguments[i]+"}"
        return Occurrence(self.name,arguments,new_text,self.position)
    def analyse(self):
        return globals()["Occurrence_"+self.name[1:]](self)     # We have to remove the initial "\" in the name of the macro.
    def __getitem__(self,a):
        return self.arguments[a]
    def __str__(self):
        return self.as_written

def SearchFitBrace(text,position,opening):
    """
    return a tuple containing the text withing the next pair of open/close brace and the position where the pair closes in text

    As an example, consider the string 
    s="Hello (Louis) how are you ?"
    SearchFitBrace(s,4,["(",")"])
    returns ('Louis', 6, 12)
    because the next brace begins at position 6, finishes at position 12 and the text within in "Louis"
    """
    close = paires[opening]
    level = 0
    giventext = text[position:]
    startPosition = position+giventext.find(opening)
    for i in range(startPosition,len(text)):
        if text[i] == opening :
            level = level+1
        if text[i] == close :
            level = level-1
        if level == 0:
            return text[startPosition+1:i],startPosition,i

def ContinueSearch(s,opening):
    r"""
    Given the string s and the position s, return True if there is still a good candidate.
    A «good» candidate is an opening bracket which is separated from the previous closing one by only elements of accepted_between_arguments. It does not takes into accounts stuff between a % and a \n 
    Return a tuple (boolean,int) where the integer is the position (in s) of the found opening bracket.
    
    Id the result is False, the returned offset is -1

    Example
    s=" \n % blahblah \n { other  "
    ContinueSearch(s,"{")
    return True and the offset of the last opening bracket
    """
    close = paires[opening]
    turtle = 0
    while turtle < len(s):
        if s[turtle]=="%":
            a=s[turtle:]
            pos = a.find("\n")
            if pos == -1:
                return False,-1
            turtle = turtle+pos
        if s[turtle] == opening :
            return True,turtle
        if s[turtle] not in accepted_between_arguments :
            return False,-1
        else :
            turtle=turtle+1
    return False,-1

def SearchArguments(s,number_of_arguments):
    r"""
    From a string of the form {A}...{B}...{C}, returns the list ["A","B","C"] where the dots are elements of the list accepted_between_arguments.
    Inside A,B and C you can have anything including the elements of the list accepted_between_arguments.
    It is important that the string s begins on an opening bracket «{»
    """
    # The way it works
    # Let be the string s=«{A}...{B}...{C}»                     (1)
    #   where A,B and C are strings and the dots are elements of the list accepted_between_arguments.
    # First we start on the first «{» and we determine the corresponding closing bracket. This is the first argument.
    #   We add in the list of argument the string s[0:fin] where fin is the position of the closing bracket
    # Then we find the next opening bracket, that is the next «{» and we determine if there is something between it and the previous closing bracket that
    #   is not in the accepted_between_arguments. In other terms, we study the content of what is represented by dots in (1)
    # We put the whole in a loop.
    # at the end, as_written is then set as the string s[0:end] where end is the last closing bracket.
    # The string s itself is never changed and all the positions of characters are computed as offset inside s.
    turtle = 0
    arguments = []
    while len(arguments) < number_of_arguments :
        try :
            arg,start,end=SearchFitBrace(s,turtle,"{")
        except :
            print "LaTeXparser Error : fitting brace not found"
            print "We were at position %s in the string"%str(turtle)
            print s
            print "------------------------------"
            raise
        arguments.append(arg)
        turtle=end+1
        if turtle >= len(s):
            as_written = s
            return arguments,as_written
        if s[turtle] <> "{":
            boo,offset = ContinueSearch(s[turtle:],"{")
            if boo:
                turtle=turtle+offset-1
            if (not boo) or (len(arguments)==number_of_arguments):
                as_written = s[0:turtle]
                return arguments,as_written

def compactization(text,accepted_between_arguments):        
    for acc in accepted_between_arguments :
        text=text.replace(acc,"")
    return text

def NextMacroCandidate(s,macro_name):
    turtle = 0
    while turtle < len(s):
        if s[turtle:turtle+len(macro_name)] == macro_name :
            return True,turtle
        if s[turtle]=="%":
            a=s[turtle:]
            pos = a.find("\n")
            if pos == -1:
                return False,-1
            turtle = turtle+pos
        turtle=turtle+1
    return False,-1

def SearchUseOfMacro(code,macro_name,number_of_arguments=None,give_configuration=False):
    r"""
    <macro_name> has to contain the initial \ of the macro. I you want to search for \MyMacro, ask for "\MyMacro"; not only "MyMacro"

    number_of_arguments is the number of arguments expected. 
                Giving a too large number produces wrong results in the following example case where \MyMacro
                is supposed to have 3 arguments :
                \MyMacro{A}{B}{C}
                {\bf An other text}
                The {\bf ...} group is not a parameter of \MyMacro, while it will be fitted as a parameter.
            It None is given, we search first for the definition and then the expected number of arguments is deduced.

            Notice that the number_of_arguments is supposed to be the number of non optional arguments. We do not count the arguments
            within [] in the number.
    We do not fit the macros that are used in the comments.

    The use of give_configuration is explained in the documentation of CodeLaTeX.search_use_of_macro

    macro_name is the name of the macro to be fitted like \MyMacro (including the backslash).

    /!\ We do not manage the case where the first argument is not immediately after the macro name, i.e.
            \MyMacro {argument} (with a space between \MyMacro and the first opening bracket)
        will be buggy.
    """
    if not macro_name in code.text_brut :
        return []
    turtle = 0
    config_turtle=0
    s = code.text_brut
    remaining = s
    use = []
    configuration=[]
    while macro_name in remaining :
        remaining=s[turtle:]
        boo,offset = NextMacroCandidate(remaining,macro_name)
        if boo :
            turtle = turtle+offset+len(macro_name)
            remaining=s[turtle:]
            try :
                arguments,as_written=SearchArguments(remaining,number_of_arguments)
            except TypeError:
                print number_of_arguments
                print remaining[0:30]
                raise
            position=turtle-len(macro_name)
            occurrence=Occurrence(macro_name,arguments,macro_name+as_written,position=turtle-len(macro_name))

            # The following test excludes the cases when we fit the \newcommand{\MyMacro}
            test=compactization(occurrence.as_written,accepted_between_arguments)
            if test[len(macro_name)] != "}":
                configuration.append(code.text_brut[config_turtle:occurrence.position])
                use.append(occurrence)
            config_turtle=position+len(occurrence.as_written)
        else :
            if give_configuration:
                configuration.append(code.text_brut[config_turtle:])
                return use,configuration
            else :
                return use
    if give_configuration:
        configuration.append(code.text_brut[config_turtle:])
        return use,configuration
    else :
        return use

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
    if type(code) == CodeLaTeX :
        return code.dict_of_definition_macros()[name]
    else :
        print "Warning: something is wrong. I'm not supposed to be here. Please contact the developer"
        return CodeLaTeX(code).dict_of_definition_macros()[name]

class Occurrence_newlabel(object):
    r"""
    takes an occurrence of \newlabel and creates an object which contains the information.

    In the self.section_name we remove "\relax" from the string.
    """
    def __init__(self,occurrence):
        self.occurrence = occurrence
        self.arguments = self.occurrence.arguments
        if len(self.arguments) == 0 :
            self.name = "Non interesting; probably the definition"
            self.listoche = [None,None,None,None,None]
            self.value,self.page,self.section_name,self.fourth,self.fifth=(None,None,None,None,None)

        else :
            self.name = self.arguments[0][0]
            self.listoche = [a[0] for a in SearchArguments(self.arguments[1][0],5)[0]]
            self.value = self.listoche[0]
            self.page = self.listoche[1]
            self.section_name = self.listoche[2].replace(r"\relax","")
            self.fourth = self.listoche[3]      # I don't know the role of the fourth argument of \newlabel
            self.fifth = self.listoche[4]       # I don't know the role of the fifth argument of \newlabel

class Occurrence_cite(object):
    def __init__(self,occurrence):
        self.label = occurrence[0]
    def entry(self,codeBibtex):
        return codeBibtex[self.label]

class Occurrence_newcommand(object):
    def __init__(self,occurrence):
        self.occurrence = occurrence
        self.number_of_arguments = 0
        if self.occurrence[1][1] == "[]":
            self.number_of_arguments = self.occurrence[1][0]
        self.name = self.occurrence[0][0]#[0]
        self.definition = self.occurrence[-1][0]

class Occurrence_input(object):
    def __init__(self,occurrence):
        self.occurrence = occurrence
        self.filename = self.occurrence[0]

class StatisticsOfTheMacro(object):
    def __init__(self,code,name):
        if type(code) != CodeLaTeX :
            code = CodeLaTeX(code)
        self.name = name
        self.definition = MacroDefinition(code,name)
        self.occurrences = SearchUseOfMacro(code,name)
        self.number_of_use = len(self.occurrences)

def RemoveComments(text):
    """
    Takes text as a tex source file and remove the comments including what stands after \end{document}
    Input : string
    Output : string
    """
    line_withoutPC = []
    # we remove the end of lines with %
    for lineC in text.split("\n"):
        ligne = lineC
        placePC = lineC.find("%")
        to_be_removed = lineC[placePC:]
        if placePC != -1:
            ligne = ligne.replace(to_be_removed,"%")
        line_withoutPC.append(ligne)
    code_withoutPC = "\n".join(line_withoutPC)

    final_code = code_withoutPC
    # Now we remove what is after \end{document}
    if "\end{document}" in final_code :
        final_code = code_withoutPC.split("\end{document}")[0]+"\end{document}"
    return final_code

class newlabelNotFound(object):
    """Exception class for CodeLaTeX.get_newlabel_value"""
    def __init__(self,label_name):
        self.label_name = label_name

def CodeLaTeXToRoughSource(codeLaTeX,filename,bibliography_bbl_filename=None,index_ind_filename=None):
    """
    Return a file containing rough self-contained sources that are ready for upload to Arxiv.
    What it does
        1. Perform all the \input recursively
        2. Remove the commented lines (leave the % symbol itself)
        3. Include the bibliography, include .bbl file (no bibtex needed)
        4. Include the index, include .ind file (no makeindex needed)
    What is does not
        1. Check for pdflatex compliance. If you are using phystricks, please refer to the documentation in order to produce a pdflatex compliant source code.

    Input 
        codeLaTeX : an object of type LaTeXparser.CodeLaTeX
        filename : the name of the file in which the new code will be written
    Optional
        bibliography_bbl_filename : the name of the .bbl file. If not give, will be guesse by changing ".tex"->".bbl" in codeLaTeX.filename
        index_ind_filename :        the name of the .bbl file. If not give, will be guesse by changing ".tex"->".ind" in codeLaTeX.filename
    Output
        Create the file named <filename>
        return the new code as LaTeXparser.CodeLaTeX

    The result is extremely hard-coded. One has not to understand it as a workable LaTeX source file.
    """
    if not bibliography_bbl_filename :
        bibliography_bbl_filename = codeLaTeX.filename.replace(".tex",".bbl")
    if not index_ind_filename :
        index_ind_filename = codeLaTeX.filename.replace(".tex",".ind")
    code_biblio = FileToCodeLaTeX(bibliography_bbl_filename)
    code_index = FileToCodeLaTeX(index_ind_filename)

    new_code = codeLaTeX.copy()
    new_code=new_code.substitute_all_inputs()
    resultBib = re.search("\\\\bibliography\{.*\}",new_code.text_brut)
    if resultBib != None :
        ligne_biblio = resultBib.group()
        new_code = new_code.replace(ligne_biblio,code_biblio.text_brut)
    resultIndex = re.search("\printindex",new_code.text_brut)
    if resultIndex != None :
        new_code = new_code.replace("\printindex",code_index.text_brut)
    new_code.filename = filename
    new_code.save()
    return new_code

class LaTeXWarning(object):
    def __init__(self,label,page):
        self.label = label
        self.page = page
        command_e="grep --color=always -n {"+self.label+"} *.tex"
        self.grep_result=commands.getoutput(command_e)
class ReferenceWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ Undefined reference \033[35;37m %s \033[35;33m à la page\033[35;40m %s \033[35;33m------"%(self.label,str(self.page))+"\n"+self.grep_result#+"\n"
class CitationWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ Undefined citation \033[35;37m %s \033[35;33m à la page\033[35;40m %s \033[35;33m------"%(self.label,str(self.page))+"\n"+self.grep_result#+"\n"
class MultiplyLabelWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ \033[35;33m Multiply defined label \033[35;33m %s --------- "%self.label+"\n"+self.grep_result#+"\n"
class TeXCapacityExceededWarning(object):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return "\033[35;34m This is a serious problem : {0} ".format(self.text)
class LabelWarning(object):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return "\033[35;32m {0} ".format(self.text)


class CodeLog(object):
    """
    Contains informations about log file.

    If your code is in a file, please use the function FileToCodeLaTeX :
    FileToCodeLog("MyFile.log")
    """
    def __init__(self,text_brut,filename=None):
        """
        self.text_brut          contains the tex code as given
        """
        self.text_brut = text_brut
        self.filename = filename
        self.undefined_references=[]
        self.undefined_citations=[]
        self.undefined_labels=[]
        self.multiply_labels=[]
        self.search_for_errors()
    def search_for_errors(self):
        print "Analysing log file",self.filename
        Warns = self.text_brut.split("Warning: ")
        for warn in Warns[1:]:
            try :
                text = warn[0:warn.find(".")]
                mots=text.split(" ")
                genre = mots[0]
                label = mots[1][1:-1]
                try :
                    page = mots[mots.index("page")+1]
                except ValueError :
                    page = -1
                if genre == "Reference" :
                    if label not in [w.label for w in self.undefined_references]:
                        self.undefined_references.append(ReferenceWarning(label,page))
                if genre == "Label" :
                    if label not in [w.label for w in self.undefined_labels]:
                        self.multiply_labels.append(MultiplyLabelWarning(label,page))
                if genre == "Citation" :
                    if label not in [w.label for w in self.undefined_citations]:
                        self.undefined_citations.append(CitationWarning(label,page))
            except ValueError :
                pass
        self.warnings = []
        self.warnings.extend(self.undefined_references)
        self.warnings.extend(self.undefined_citations)
        self.warnings.extend(self.multiply_labels)

        self.maybeMore ="LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
        if self.maybeMore in self.text_brut:
            self.warnings.append(LabelWarning(self.maybeMore))

        self.TeXcapacityexeeded="TeX capacity exceeded"
        if self.TeXcapacityexeeded in self.text_brut:
            self.warnings.append(TeXCapacityExceededWarning(self.TeXcapacityexeeded))


        self.probs_number=len(self.warnings)
    def tex_capacity_exeeded(self):
        return self.TeXcapacityexeeded in self.text_brut
    def __str__(self):
        a=[]
        for warn in self.warnings :
            a.append(warn.__str__())
        if self.probs_number > 1:
            a.append("Il reste encore %s problèmes à régler. Bon travail."%str(self.probs_number))
        if self.probs_number == 1:
            a.append("C'est ton dernier problème à régler. Encore un peu de courage !")
        return "\n".join(a)

def ConvertToUTF8(text):
    try :
        return unicode(text,"utf_8")
    except TypeError :
        return text

def ListOfCitation(filelist):
    r"""
    From a list of files, return the list of arguments in \cite{...}.
    """
    l=[]
    new_filelist=[a+".tex" for a in filelist]
    for f in new_filelist :
        codeLaTeX =FileToCodeLaTeX(f)
        occurences = codeLaTeX.analyse_use_of_macro("\cite",1)
        print "537",f
        print "536",occurences
        for occ in occurences :
            l.append(occ.label)
    return l

def CreateBibtexFile(big_bibtex_file,small_bibtex_file,list_of_files):
    r"""
    Put in small_bibtex_file the bibex code needed for all the citations in list_of_files. Take the bibtex code from big_bibtex_file

    An error is raised if
    - a citation has no code in big_bibtex_file         (it is raised in CodeBibtex.extract_list)
    - the code is already in small_bibtex_file, but is different to the one in big_bibtex_file

    A warning is written if 
    - an entry in small_bibtex_file is not used in the list_of_files.
    """
    list_of_citations=ListOfCitation(list_of_files)
    print "554",list_of_files
    print "554",list_of_citations
    big_bibtex=FileToCodeBibtex(big_bibtex_file)
    extracted_big=big_bibtex.extract_list(list_of_citations)
    small_bibtex=FileToCodeBibtex(small_bibtex_file)
    for label in small_bibtex.entry_dict.keys() :
        if label not in list_of_citations:
            print "Useless entry : %s"%label
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
                print "I have no entry labelled %s"%label
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
                    print 
                    raise NameError,"Different texts for the label %s"%entry.label
            dico[entry.label]=entry
        return EntryListToCodeBibtex(dico.values())

class CodeLaTeX(object):
    """
    Contains the informations about a LaTeX code.

    This class does not take track of the comments in the code. The symbol % is however kept because it
    is important for paragraphs in LaTeX.

    If your code is in a file, use the function FileToCodeLaTeX:
    FileToCodeLaTeX("MyFile.tex")
    returns a CodeLaTeX instance.
    """
    # In a previous version, we were keeping the comments, but it caused some difficulties because, for example, we had to only perform the
    # replacements outside the comments, so that we had to perform replacements line by line. It was painfully slow. 
    # If you have any idea how to keep track of the comments without slow down the process, please send a patch :)
    def __init__(self,given_text,filename=None):
        """
        self.text_brut          contains the tex code as given, without the comments
        """
        # If you change something here, it has to be changed in append_file.
        self.given_text = given_text
        self.text_brut = ConvertToUTF8(RemoveComments(self.given_text))
        self._dict_of_definition_macros = {}
        self._list_of_input_files = []
        self.filename = filename
    def copy(self):
        """
        Return a copy of self in a new object
        """
        return CodeLaTeX(self.text_brut)
    def save(self,filename=None,preamble=True):
        """
        Save the code in a file.
        
        Optional <filename> provides a file name that overrides the self.filename. If none of filename and self.filename are give, an exception is raised.
        Optional preamble (boolean) : yes or no, do we add the preamble speaking about the scripts.
        
        """
        
        preamble = r"""% This file is automatically generated by some pre-compilation scripts.
%See
%http://gitorious.org/phystricks
%http://gitorious.org/phystricks-doc/phystricks-doc
%http://gitorious.org/latexparser
%Please contact the author at moky.math@gmail.com for asking original source file and scripts.
%
        """
        written_text=self.text_brut
        if preamble :
            written_text=preamble+written_text
        if filename:
            self.filename=filename
        else :
            filename = self.filename
        f = codecs.open(filename,"w","utf_8")
        f.write(written_text)
        f.close()
    def get_newlabel_value(self,label_name):
        r"""
        Assumes that self is a .aux file. Return the value associated to the line \newlabel{<label_name>}

        It it appears many times, return the last time, and prints a warning.

        If not found, raise an newlabelNotFound exception 
        """
        list_newlabel = self.analyse_use_of_macro("\\newlabel",2)
        if label_name not in [x.name for x in list_newlabel] :
            raise newlabelNotFound(label_name)
        list_interesting  = [x for x in list_newlabel if x.name==label_name]
        if len(list_interseting) > 1 :
            print "Warning : label %s has %s different values"%(label_name,str(len(list_interesting)))
        return list_interesting[-1].value
    def search_use_of_macro(self,name,number_of_arguments=None,give_configuration=False):
        r"""
        Return a list of Occurrence of a given macro. You have to include the "\" in the name, for example
        codeLaTeX.search_use_of_macro("\MyMacro",2)
        is the good way to study the use of macro \MyMacro, provided that it has exactly 2 arguments.

        Optional argument: number_of_arguments=None
        If no occurrence are found, return an empty list.

        If give_configuration is True, return a tuple of two lists. The first list is the same as with give_configuration=False, and the second gives the 
        text between the occurrences. The ith element of the configuration list is what precedes the ith element of the occurrence list.
        The configuration list has one more element.
        The following has to be true
        self.text_brut==configuration[0]+occurrence[0]+...+configuration[n]+occurrence[n]+configuration[n+1]
        """
        A = SearchUseOfMacro(self,name,number_of_arguments,give_configuration)
        return A
    def analyse_use_of_macro(self,name,number_of_arguments=None):
        """
        Provide a list of analyse of the occurrences of a macro.

        Optional argument: number_of_arguments=None, to be passed to search_use_of_macro
        """
        return [occurence.analyse() for occurence in self.search_use_of_macro(name,number_of_arguments) ]
    def macro_definition(self,name):
        return MacroDefinition(self,name)
    def statistics_of_the_macro(self,name):
        return StatisticsOfTheMacro(self,name)
    def dict_of_definition_macros(self):
        r"""
        Returns a dictionnary wich gives, for each name of macros found to be defined in self.text, the occurrence 
        in which it was defined.
        If X is the output of dict_of_definition_macro, X.keys() is the list of the names of the macros and
        X.values() is the list of definition (type Occurrence_newcommand).

        The macro Foo is "defined" in the text when "Foo" comes as first argument of a definition command.
        (cf. the global variable definition_commands) Typically when
        \\newcommand{\Foo}[2]{bar}
        or
        \\renewcommand{\Foo}{bar}
        """
        if self._dict_of_definition_macros == {} :
            print "Je réinvente la roue"
            dico = {}
            for definer in definition_commands :            
                for occurrence in self.search_use_of_macro(definer,3):
                    newcommand = Occurrence_newcommand(occurrence)
                    name = newcommand.name
                    if name in dico.keys() :
                        print "%s was already defined !!"%name
                    else :
                        dico[name]=newcommand
            self._dict_of_definition_macros = dico
        return self._dict_of_definition_macros
    def list_of_input_files(self):
        if self._list_of_input_files == []:
            list = []
            for occurrence in self.search_use_of_macro("\input",1):
                list.append(occurrence.analyse().filename)
            self._list_of_input_files = list
        return self._list_of_input_files
    def substitute_input(self,filename,text=None):
        r""" 
        replace \input{<filename>} by <text>.

        By default, it replaces by the content of <filename> (add .tex if no extension is given) which is taken in the current directory.

        Some remarks
        1. This function is not recursive
        2. It does not really check the context. A \input in a verbatim environment will be replaced !
        3. If a file is not found, a IOError exception is raised
        """
        list = []
        if text==None:
            strict_filename = filename
            if "." not in filename:
                strict_filename=filename+".tex"
            try:
                text = "".join( open(strict_filename,"r") )[:-1]    # Without [:-1] I got an artificial empty line at the end.
            except IOError :
                print "Warning : file %s not found."%strict_filename
                raise
        list_input = self.search_use_of_macro("\input",1)
        for occurrence in list_input:
            x = occurrence.analyse()
            if x.filename == filename :         # Create the list of all the texts of the form \input{<filename>}
                list.append(x.occurrence.as_written)
        A = CodeLaTeX(self.text_brut)
        for as_written in list :
            A=A.replace(as_written,text)
        return A
    def substitute_all_inputs(self):
        r"""
        Recursively change all the \input{...} by the content of the corresponding file. 
        Return a new object LaTeXparser.CodeLaTeX
        """
        A = CodeLaTeX(self.text_brut)
        list_input = A.search_use_of_macro("\input",1)
        while list_input :
            for occurrence in list_input :
                x = occurrence.analyse()
                A = A.substitute_input(x.filename)
            list_input = A.search_use_of_macro("\input",1)
        return A
    def change_macro_argument(self,macro_name,n,func,n_args):
        r"""
        Apply the function <func> to the <n>th argument of each use of <macro_name>.

        return a new_object CodeLaTeX
        """
        list_occurrences,configuration=self.search_use_of_macro(macro_name,n_args,give_configuration=True)
        a=""
        for i in range(len(list_occurrences)):
            a=a+configuration[i]+list_occurrences[i].change_argument(n,func).as_written
        a=a+configuration[-1]
        return CodeLaTeX(a)
    def change_labels_refs(self,func):
        r"""
        Change \ref{MyLabel}, \eqref{MyLabel} and \label{MyLabel} applying func to the argument.
        """
        x=self.change_macro_argument(r"\ref",1,func,1)
        y=x.change_macro_argument(r"\eqref",1,func,1)
        z=y.change_macro_argument(r"\label",1,func,1)
        self.__init__(z.text_brut)
    def remove_macro_content(self,macro_name,number_of_arguments):
        r"""
        Remove the presence of a macro (not its definition). 
        Example

        Hello \MyMacro{guy} how do you do ?

        will become 
        Hello how do you do ?

        Return a new LaTeXparser.CodeLaTeX object.
        """
        A = self.copy()
        liste_occurrences = A.search_use_of_macro(macro_name,number_of_arguments)
        for occurrence in liste_occurrences :
            A=A.replace(occurrence.as_written,"")
        return A
    def remove_macro_name(self,macro_name,number_of_arguments):
        r"""
        Remove the macro name, but leaves the argument.
        Example

        Hello \MyMacro{guy} how do you do ?

        will become 
        Hello guy how do you do ?

        This function only works with a macro which has only one argument.
        """
        A = self.copy()
        liste_occurrences = A.search_use_of_macro(macro_name,number_of_arguments)
        for occurrence in liste_occurrences :
            A=A.replace(occurrence.as_written,occurrence.arguments[0])
        return A
    def find(self,arg):
        return self.text.find(arg)
    def replace(self,textA,textB):
        """ Replace textA by textB including in the comments """
        textA=ConvertToUTF8(textA)
        textB=ConvertToUTF8(textB)
        new_text = self.text_brut.replace(textA,textB)
        return CodeLaTeX(new_text)
    def append_file(self,filename=None,filenames=None):
        """
        Append the content of a file to the current LaTeX code. Return a new object.

        If filename is given, add only this file
        If filenames is given, add all the files.

        See the method __add__
        """
        if filename :
            if ".tex" not in filename :
                filename = filename+".tex"
            new = self+FileToCodeLaTeX(filename)
            self.__init__(new.text_brut)
        if filenames :
            for i in range(len(filenames)):
                if ".tex" not in filenames[i] :
                    filenames[i] = filenames[i]+".tex"
            a = ""
            for f in filenames :
                a=a+FileToText(f)
            add_given_text=a
            self.__init__(self.given_text+add_given_text)
    def rough_source(self,filename,bibliography_bbl_filename=None,index_ind_filename=None):
        """
        Return the name of a file where there is a rough latex code ready to be published to Arxiv
        See the docstring of LaTeXparser.CodeLaTeXToRoughSource
        """
        return CodeLaTeXToRoughSource(self,filename,bibliography_bbl_filename,index_ind_filename)
    def __add__(self,other):
        new_given_text=self.given_text+other.given_text
        return CodeLaTeX(new_given_text)
