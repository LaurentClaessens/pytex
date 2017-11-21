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

# copyright (c) Laurent Claessens, 2010,2012-2017
# email: laurent@claessens-donadello.eu

import re
from src.Occurrence import Occurrence
from src.Utilities import dprint

paires = { "{":"}","[":"]","`":"'"}
accepted_between_arguments = ["%","\n"," ","    "] # the last one is a TAB

def compactization(text,accepted_between_arguments):        
    for acc in accepted_between_arguments :
        text=text.replace(acc,"")
    return text


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
            print("latexparser Error : fitting brace not found")
            print("We were at position %s in the string"%str(turtle))
            print(s)
            print("------------------------------")
            raise
        arguments.append(arg)
        turtle=end+1
        if turtle >= len(s):
            as_written = s
            return arguments,as_written
        if s[turtle] != "{":
            boo,offset = ContinueSearch(s[turtle:],"{")
            if boo:
                turtle=turtle+offset-1
            if (not boo) or (len(arguments)==number_of_arguments):
                as_written = s[0:turtle]
                return arguments,as_written

def NextMacroCandidate(s,macro_name,search_macro_name=None):
    """
    return the a tuple (boolean,integer,boolena) saying 
    1. if macro_name is present in string s
    2. where is it
    3. if this is in a comment  (False if there are no matching macro)

    This macro does not return results that are inside comments.
    """
    if search_macro_name==None:
        search_macro_name=re.compile(re.escape(macro_name)+"[^A-Za-z]").search
    result=search_macro_name(s)
    if not result :
        return False,-1,False
    k=result.start()

    # init_line is the position at which the line begins;
    # we are going to check if there is "[^\]%" between the begining
    # of the line and my macro.
    init_line=s[0:k].rfind("\n")
    if init_line==-1:
        init_line=0
    candidate=s[init_line:k]
    search_comment_pc=re.compile("[^\\\]%").search
    result=search_comment_pc(candidate)
    if result :
        return True,k,True
    return True,k,False

def SearchUseOfMacro(code,macro_name,number_of_arguments=None,give_configuration=False,fast=False):
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

    The use of give_configuration is explained in the documentation of LatexCode.search_use_of_macro

    macro_name is the name of the macro to be fitted like \MyMacro (including the backslash).

    /!\ We do not manage the case where the first argument is not immediately after the macro name, i.e.
            \MyMacro {argument} (with a space between \MyMacro and the first opening bracket)
        will be buggy.

    If fast is true, make more assumptions on the LaTeX code. Like no space, no \ and no {} inside or between the arguments.
             Only works with exactly one argument up to now :
    """
    use=[]
    s = code.text_brut
    if fast :       

        e_macro_name=re.escape(macro_name)
        results=re.finditer(e_macro_name+"{",s)

        for res in results :
            start = res.start()
            # Only works with exactly one argument up to now :
            end=s.find("}",start)
            as_written = s[start:end]           # This as_written contains the macro name; in the non-fast version, it does not contain.
            arguments=[s[start+len(macro_name):end]]
            occurrence=Occurrence(macro_name,arguments,as_written,position=start)
            use.append(occurrence)
        return use

    search_macro_name=re.compile(re.escape(macro_name)+"[^A-Za-z@]").search
    if not macro_name in s :
        return []
    turtle = 0
    config_turtle=0
    remaining = s
    use = []
    configuration=[]
    boo=True
    while boo:
        remaining=s[turtle:]
        boo,offset,in_comment = NextMacroCandidate(remaining,macro_name,search_macro_name=search_macro_name)
        if boo :
            turtle = turtle+offset+len(macro_name)
            remaining=s[turtle:]
            if not in_comment :
                try :
                    arguments,as_written=SearchArguments(remaining,number_of_arguments)
                except TypeError:
                    print(number_of_arguments)
                    print(remaining[0:30])
                    raise
                position=turtle-len(macro_name)
                occurrence=Occurrence(macro_name,arguments,macro_name+as_written,position=turtle-len(macro_name))

                # The following test excludes the cases when we fit the \newcommand{\MyMacro}
                test=compactization(occurrence.as_written,accepted_between_arguments)
                if test[len(macro_name)] != "}":
                    configuration.append(code.text_brut[config_turtle:occurrence.position])
                    use.append(occurrence)
                config_turtle=position+len(occurrence.as_written)
        else :      # if not boo
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
