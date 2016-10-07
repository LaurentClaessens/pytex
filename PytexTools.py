# -*- coding: utf8 -*-

###########################################################################
#   This is part of the package latexparser
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

# copyright (c) Laurent Claessens, 2010, 2012-2015
# email: moky.math@gmail.com

"""
Contains tools (using latexparser) intended to create good plugins for pytex.

pytex is a non-yet published pre-compilation system. Don't try to understand what this module serves to.
"""

import os
import hashlib
from xml.dom import minidom
import latexparser

# TODO : there should be a possibility to compile "up to all references are correct" from here. 
#       I mean : the checking algorithm should be here.
class Compilation(object):
    """
    Launch the compilation of a document in various ways.
    Takes a filename as argument

    Optional boolean argument <nocompilation>. If set to True, the compilations are not actually done, but the command line is printed.

    Usage examples
    X=latexparser.Compilation("MyLaTeXFile.tex")    # Creates the Compilation object
    X.bibtex()                  # Apply bibtex
    X.chain_dvi_ps_pdf()                # Produce the pdf file
    """
    def __init__(self,filename,nocompilation=False,pdflatex=True,dvi=False):
        import os
        self.filename=filename
        self.nocompilation=nocompilation
        self.dirname=os.path.dirname(self.filename)
        self.basename=os.path.basename(self.filename)
        self.generic_basename = self.basename[:self.basename.rindex(".")]
        self.generic_filename = os.path.join(self.dirname,self.generic_basename)
        #self.generic_filename = self.filename[:self.filename.rindex(".")]
        #self.generic_basename=os.path.split(self.generic_filename)[1]
    def do_it(self,commande_e):
        commande_e=commande_e.encode("utf8")
        print("*** external :",commande_e)
        if self.nocompilation :
            print("not executed")
        else :
            os.system(commande_e)
    def bibtex(self):
        # absolute pathname.
        commande_e="bibtex "+self.generic_basename
        self.do_it(commande_e)
    def makeindex(self):
        commande_e="makeindex "+self.generic_basename
        self.do_it(commande_e)
    def nomenclature(self):
        commande_e="makeindex -s nomencl.ist -o "+self.generic_basename+".nls "+self.generic_basename+".nlo"        
        self.do_it(commande_e)
    def special_stuffs(self):
        self.bibtex()
        self.makeindex()
        self.nomenclature()
    def latex(self):
        program=u"/usr/bin/pdflatex -synctex=1   -shell-escape"
        # The following line does not work without the u"...". Even if {0} and {1} are type unicode
        commande_e=u"""{0} {1} """.format(program,self.filename)
        self.do_it(commande_e)

    def chain_dvi_ps(self,papertype="a4"):
        raise DeprecationWarning
        """
        The chain tex->div->ps

        After compiling by self.latex(), produce a ps file from the dvi by the command
        dvips -t <papertype> <self.filename>.dvi
        
        Optional parameter : papertype is "a4" by default
        """
        self.latex()
        commande_e="dvips -t %s %s.dvi"%(papertype,self.generic_filename)
        print(commande_e)
        self.do_it(commande_e)
    def chain_dvi_ps_pdf(self,papertype="a4",quiet=True):
        raise DeprecationWarning
        """
        The chain tex->dvi-ps->pdf 
        This is more or less the only way to produce a pdf file containing pstricsk figures and hyperref links.

        After having produced the ps by self.chain_dvi_ps(), produce a pdf file from the ps by the command
        ps2pdf <self.filename>.ps
        
        Optional parameter : papertype is "a4" by default (to be passed to dvips)
        """
        self.chain_dvi_ps(papertype)
        commande_e="ps2pdf "+self.generic_filename+".ps" 
        if not quiet:
            print(commande_e,"...")
        self.do_it(commande_e)
    def latex_more(self):
        self.special_stuffs()
        self.latex()
        self.special_stuffs()

def ChangeLabelsAndRef(codeLaTeX,func):
    r"""
    Apply the function func to each argument of \label, \ref, \eqref in codeLaTeX.

    return a new object latexparser.LatexCode
    """
    list_occurrences = codeLaTeX.search_use_of_macro("\label",1)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class CodeBox(dict):
    """
    This class is intended to keep some portions of LaTeX code in a fresh box, allowing to retrieve them later.

    You create your box with
    box = CodeBox("MyDict")
    the name of the box is "MyDict". 

    The line to be put in your LaTeX file is like
    \PutMyDict{foo}{an example box}
    \PutMyDict{bar}{another example box}
    If these lines are contained in codeLaTeX, you do
    box.put(codeLaTeX,"foo")
    and the first line will be replaced by the content of box["an example box"] while the second will be replaced by "" (empty string).
    If you do
    box.put(codeLaTeX,"bar")
    the first line will be replaced by "" (empty string) while the second will be replaced by the content of box["another example box"].
    """
    def __init__(self,name):
        dict.__init__({})
        self.name=name
        self.put_macro="\Put"+self.name
    def feed(self,xmlCode):
        r"""
        Parse xmlCode and fill the dictionary.

        Example. You feed your box with a XML file containing
        <CodeBox label="an example box">
        This is my \LaTeX\ code.
        </CodeBox>
        Then the command
        box.feed(filename)
        adds the text «This is my \LaTeX\ code» in the dictionary with the key «an example box»
        """
        xmlCode_corrected=xmlCode.replace("&","[PytexSpecial amp]")
        c=xmlCode_corrected.encode("utf-8")
        dom = minidom.parseString(c)
        for box in dom.getElementsByTagName("CodeBox"):
            dict_name = box.getAttribute("dictName")
            if dict_name == self.name :
                label = box.getAttribute("label")
                pre_code = getText(box.childNodes)
                code = "\n".join(pre_code.split("\n")[1:-1])    # Because minidom adds an empty line at first and last position.
                self[label]=latexparser.LatexCode(code.replace("[PytexSpecial amp]","&"))
    def put(self,codeLaTeX,tag):
        # This function is added to the plugin list of Request when using the method Request.create_magic_box
        r"""
        Substitute the dictionary inside codeLaTeX. 
            If we continue the example of the method CodeBox.feed, the line
            \PutMyDict{mylabel} 
            will be changed to
            This is my \LaTeX\ code.
        You can (this is the aim!) substitute the code at several places.

        return a new object latexparser.LatexCode
        """
        A=codeLaTeX.copy()
        liste_occurrences = A.search_use_of_macro(self.put_macro,2)
        for occurrence in liste_occurrences :
            tags=occurrence.arguments[0].split(",")
            if tags == [""] or tag in tags :    # If we don't mention a tag, they are all good
                try :
                    label=occurrence.arguments[1]
                    B=self[label]
                    B=self.put(B,tag)           # This function is recursive !
                    A=A.replace(occurrence.as_written,B.text_brut)
                except IndexError :
                    print("PytexTools error : \Put... needs two arguments. Don't forget the tag")
                    print(occurrence.as_written)
                    raise
            else :
                A=A.replace(occurrence.as_written,"")
        return A

def FileToCodeBox(filename,boxname):
    """
    Return a CodeBox object fed by the content of the given file.
    """
    magic_box_code = latexparser.FileToText(filename)
    magic_box = CodeBox(boxname)
    magic_box.feed(magic_box_code)
    return magic_box

def PytexNotIn(name,codeLaTeX):
    r"""
    Return a latexparser.LatexCode object build from codeLaTeX and changing the occurrences of
    \PytexNotIn{name1,name2,...}{code}
    by <code> if name is not in the liste name1, name2, ... Else, remove it completely.

    This acts like some inline CodeBox. This is the symmetric of PytexOnlyIn
    """
    A = codeLaTeX.copy()
    occurrences = A.search_use_of_macro("\PytexNotIn",2)
    for occurrence in occurrences :
        tags=occurrence.arguments[0].split(",")
        if name not in tags :
            code=occurrence.arguments[1]
            A=A.replace(occurrence.as_written,code)
        else :
            A=A.replace(occurrence.as_written,"")
    return A

def PytexOnlyIn(name,codeLaTeX):
    r"""
    Return a latexparser.LatexCode object build from codeLaTeX and changing the occurrences of
    \PytexOnlyIn{name1,name2,...}{code}
    by <code> if name is in the liste name1, name2, ... Else, remove it completely.

    This acts like some inline CodeBox
    """
    A = codeLaTeX.copy()
    occurrences = A.search_use_of_macro("\PytexOnlyIn",2)
    for occurrence in occurrences :
        tags=occurrence.arguments[0].split(",")
        if name in tags :
            code=occurrence.arguments[1]
            A=A.replace(occurrence.as_written,code)
        else :
            A=A.replace(occurrence.as_written,"")
    return A

class CodeFactory(object):
    """
    Contain what one needs to build LaTeX code from files, plugin, magical boxes, ...

    For most of methods, see the docstring of the corresponding method in latexparser.LatexCode
    """
    def __init__(self):
        self.codeLaTeX=latexparser.LatexCode("")
        self.plugin_list = []
        self.code_box_list = []
        self.fileTracking = FileTracking()
    def is_file_changed(self,filename=None,filenames=None):
        return self.fileTracking.is_file_changed(filename,filenames)
    def append_file(self,filename=None,filenames=None):
        self.codeLaTeX.append_file(filename,filenames)
    def apply_all_plugins(self):
        text=self.codeLaTeX.text_brut
        for plugin in self.plugin_list :
            text = plugin(text)
        self.codeLaTeX = latexparser.LatexCode(text)
    def apply_all_code_box(self,tag):
        A=self.codeLaTeX.copy()
        for box in self.code_box_list:
            A=box.put(self.codeLaTeX,tag)
        self.codeLaTeX=A
    def apply_all(self,tag):
        # TODO : this function should be recursive and apply plugin/code_box as long as necessary, so that one can nest them.
        r"""
        1. Substitute all the \input
        2. Apply the plugins
        3. Apply the code_box
        4. Adapt PytexNotIn and PytexOnlyIn
        5. Write the FileTracking xml file
        """
        self.codeLaTeX = self.codeLaTeX.substitute_all_inputs()
        self.apply_all_plugins()
        self.apply_all_code_box(tag)
        self.codeLaTeX = PytexNotIn(tag,self.codeLaTeX)
        self.codeLaTeX = PytexOnlyIn(tag,self.codeLaTeX)
        FileTracking().save()
    def save(self,filename):
        self.codeLaTeX.save(filename)

def FileToSha1sum(f):
    text = str(open(f).read())
    return hashlib.sha1(text).hexdigest()

class FileTracking(object):
    ELEMENT_FOLLOWED_FILES = "Followed_files"
    TAG_FICHIER="fichier"
    xml_filename = "pytextools.xml"
    old_sha={}
    try :
        root = minidom.parse(xml_filename)
        fileNodes = root.getElementsByTagName(ELEMENT_FOLLOWED_FILES)
        for fileNode in fileNodes: 
            for fich in fileNode.getElementsByTagName(TAG_FICHIER):
                old_sha[fich.getAttribute("name")]=fich.getAttribute("sha1sum")
    except :
        print("XML file is probably empty.")
    sha={}
    for k in old_sha.keys():
        sha[k]=old_sha[k]
    def _is_file_changed(self,filename):
        sha_now="XXX"
        try :
            sha_now = FileToSha1sum(filename)
        except IOError :
            pass
        FileTracking.sha[filename]=sha_now
        if filename not in FileTracking.old_sha.keys() :
            return True
        return not sha_now == FileTracking.old_sha[filename]
    def is_file_changed(self,filename=None,filenames=None):
        if filename :
            return self._is_file_changed(filename)
        if filenames :
            boos = [self._is_file_changed(f) for f in filenames]
            return True in boos
    def xml(self):
        """Return the xml code to be written in pytextools.xml"""
        followed_files_xml = minidom.Document()
        the_sha = followed_files_xml.createElement(FileTracking.ELEMENT_FOLLOWED_FILES)
        for f in FileTracking.sha.keys():
            xml = followed_files_xml.createElement(FileTracking.TAG_FICHIER)
            xml.setAttribute('name',f)
            xml.setAttribute('sha1sum',FileTracking.sha[f])
            the_sha.appendChild(xml)
        followed_files_xml.appendChild(the_sha)
        return followed_files_xml.toprettyxml()
    def save(self,medicament=None):
        # The medicament optional argument is in order to avoid to save if --no-compilation if passed to pytex. In that case, the changes are not taken into account,
        # and thus the last "used" sha1sum is the one which is still in the file.
        faire = True
        if medicament:
            if medicament.Sortie.nocompilation :
                faire = False
        if faire :
            open(FileTracking.xml_filename,"w").write(self.xml())

class Plugin(object):
    def __init__(self,fun,hook_name):
        self.fun=fun
        self.hook_name=hook_name
    def __call__(self,A):
        return self.fun(A)

class Request(object):
    """ Contains what a lst_foo.py file has to contain """
    def __init__(self,name=None):
        self.plugin_list = []
        self.medicament=None
        self.medicament_plugin=None
        self.original_filename = ""
        self.ok_filenames_list = []
        self.prerequiste_list = []
        self.fileTracking=FileTracking()
        self.new_output_filename=None
    def is_file_changed(self,f):
        return self.fileTracking.is_file_changed(f)
    def create_magic_box(self,filename,boxname,name=None):
        if name==None :
            name=self.name
        self.magic_box=FileToCodeBox(filename,boxname)
        self.plugin_list.append(self.magic_box.put)
    def run_prerequistes(self,arg):
        for plug in self.prerequiste_list:
            plug(arg)
        self.fileTracking.save()
    def add_plugin(self,fun,hook_name):
        self.plugin_list.append(Plugin(fun,hook_name))

class Array(object):
    def __init__(self,dic):
        """
        'dic' is the dictionary that gives the texts to be put in the array.

        (0,0) (1,0) (2,0) (3,0) etc
        (0,1) (1,1) (2,1) (3,1) etc 
        etc
        """
        self.dic=dic
        self.nlines=max(  [x[1] for x in self.dic.keys()] )+1
        self.ncols=max(  [x[0] for x in self.dic.keys()] )+1
    def latex(self):
        a=[]
        a.append("\\begin{array}[]")
        a.append("{|c|")
        for i in range(0,self.ncols-1):
            a.append("c|")
        a.append("}\n\hline\n""")

        for i in range(0,self.nlines):
            for j in range(0,self.ncols):
                a.append(self.dic[j,i])
                a.append("&")
            a=a[:-1]   # The last '&' has to be removed. Border effect.
            a.append("\\\\"+"\n"+"\hline"+"\n")


        a.append("\end{array}")
        return "".join(a)

def script_mark_dict(C):
    """
    A dictionary of tuple ('text','position') where
    'text' is the content between two "% SCRIPT MARK" and 'position' is the position of the beginning.
    """
    dic={}
    dic["init"]=0
    lp="init"
    lignes=C.splitlines()
    for i,l in enumerate(lignes) :
        if l.startswith("% SCRIPT MARK"):
            dic[l]=i+1
            dic[lp]=(dic[lp],i+1)
            lp=l
    dic[lp]=(dic[lp],len(lignes))
    return dic

class keep_script_marks(object):
    """
    The file "mazhe.tex" has some "SCRIPT MARK" lines that give the structure of the document.

    Notice that whatever the order of the marks is in the given list, it will respect the order of requested file.

    As plugin, this is supposed to be used before pytex.
    (from January, 12, 2015)
    """
    def __init__(self,keep_mark_list):
        self.keep_mark_list=keep_mark_list
    def __call__(self,text):
        smd=script_mark_dict(text)
        B=[]
        lignes=text.splitlines()
        # Select the usefull marks and sort them.
        marks=[  x for x in smd.keys() if x in self.keep_mark_list ]
        marks.sort(key=lambda a:smd[a][0])
        for mark in marks :
            a=smd[mark][0]
            b=smd[mark][1]
            B.extend(  lignes[a:b] )

            addtext=lignes[a:b]

        new_text= "\n".join(B)
        return new_text

def accept_all_input(medicament):
    medicament.accept_input=lambda x: True

