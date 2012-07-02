# -*- coding: utf8 -*-

###########################################################################
#   This is part of the package LaTeXparser
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

# copyright (c) Laurent Claessens, 2010, 2012
# email: moky.math@gmail.com

"""
Contains tools (using LaTeXparser) intended to create good plugins for pytex.

pytex is a non-yet published pre-compilation system. Don't try to understand what this module serves to.
"""

import os
import hashlib
from xml.dom import minidom
import LaTeXparser

# TODO : there should be a possibility to compile "up to all references are correct" from here. 
#       I mean : the algorithm of checking should be here.
class Compilation(object):
    """
    Launch the compilation of a document in various ways.
    Takes a filename as argument

    Optional boolean argument <nocompilation>. If set to True, the compilations are not actually done, but the command line is printed.

    Usage examples
    X=LaTeXparser.Compilation("MyLaTeXFile.tex")    # Creates the Compilation object
    X.bibtex()                  # Apply bibtex
    X.chain_dvi_ps_pdf()                # Produce the pdf file
    """
    def __init__(self,filename,nocompilation=False,pdflatex=True,dvi=False):
        import os
        self.pdflatex=pdflatex
        self.dvi=dvi
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
        if self.nocompilation :
            print commande_e
        else :
            os.system(commande_e)
    def bibtex(self):
        commande_e="bibtex "+self.generic_filename
        self.do_it(commande_e)
    def makeindex(self):
        commande_e="makeindex "+self.generic_filename
        self.do_it(commande_e)
    def nomenclature(self):
        commande_e="makeindex -s nomencl.ist -o "+self.generic_filename+".nls "+self.generic_filename+".nlo"        
        self.do_it(commande_e)
    def special_stuffs(self):
        self.bibtex()
        self.makeindex()
        self.nomenclature()
    def latex(self):
        """Produce a dvi or pdf file using latex or pdflatex"""
        if self.pdflatex :
            program="/usr/bin/pdflatex"
        else :
            program="/usr/bin/latex --src-specials"
        commande_e="""{0} {1} """.format(program,self.filename)
        self.do_it(commande_e)
        output_file=os.path.join(self.dirname,self.generic_basename+".@pyXXX")
        new_output_file=os.path.join(self.dirname,"0-"+self.generic_basename+".@pyXXX")
        #output_file=self.directory+"/"+self.generic_basename+".@pyXXX"
        #new_output_file=self.directory+"/0-"+self.generic_basename+".@pyXXX"
        if self.pdflatex:
            extension=".pdf"
        else :
            extension=".dvi"
        output_file=output_file.replace(".@pyXXX",extension)
        new_output_file=new_output_file.replace(".@pyXXX",extension)
        import shutil
        shutil.copy2(output_file,new_output_file)
        if self.pdflatex:
            output_pdfsync=output_file+"sync"
            new_output_pdfsync=new_output_file+"sync"
            if not os.path.exists(output_pdfsync):
                raise NameError,"Are you using pdflatex without \usepackage{pdfsync} ?? I don't believe it !"
            shutil.copy2(output_pdfsync,new_output_pdfsync)
    def chain_dvi_ps(self,papertype="a4"):
        """
        The chain tex->div->ps

        After compiling by self.latex(), produce a ps file from the dvi by the command
        dvips -t <papertype> <self.filename>.dvi
        
        Optional parameter : papertype is "a4" by default
        """
        self.latex()
        commande_e="dvips -t %s %s.dvi"%(papertype,self.generic_filename)
        self.do_it(commande_e)
    def chain_dvi_ps_pdf(self,papertype="a4",quiet=True):
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
            print commande_e,"..."
        self.do_it(commande_e)
    def latex_more(self):
        self.special_stuffs()
        self.latex()
        self.special_stuffs()

def ChangeLabelsAndRef(codeLaTeX,func):
    r"""
    Apply the function func to each argument of \label, \ref, \eqref in codeLaTeX.

    return a new object LaTeXparser.CodeLaTeX
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
        dom = minidom.parseString(xmlCode_corrected)
        for box in dom.getElementsByTagName("CodeBox"):
            dict_name = box.getAttribute("dictName")
            if dict_name == self.name :
                label = box.getAttribute("label")
                pre_code = getText(box.childNodes)
                code = "\n".join(pre_code.split("\n")[1:-1])    # Because minidom adds an empty line at first and last position.
                self[label]=LaTeXparser.CodeLaTeX(code.replace("[PytexSpecial amp]","&"))
    def put(self,codeLaTeX,tag):
        # This function is added to the plugin list of Request when using the method Request.create_magic_box
        r"""
        Substitute the dictionary inside codeLaTeX. 
            If we continue the example of the method CodeBox.feed, the line
            \PutMyDict{mylabel} 
            will be changed to
            This is my \LaTeX\ code.
        You can (this is the aim!) substitute the code at several places.

        return a new object LaTeXparser.CodeLaTeX
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
                    print "PytexTools error : \Put... needs two arguments. Don't forget the tag"
                    print occurrence.as_written
                    raise
            else :
                A=A.replace(occurrence.as_written,"")
        return A

def FileToCodeBox(filename,boxname):
    """
    Return a CodeBox object fed by the content of the given file.
    """
    magic_box_code = LaTeXparser.FileToText(filename)
    magic_box = CodeBox(boxname)
    magic_box.feed(magic_box_code)
    return magic_box

def PytexNotIn(name,codeLaTeX):
    r"""
    Return a LaTeXparser.CodeLaTeX object build from codeLaTeX and changing the occurrences of
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
    Return a LaTeXparser.CodeLaTeX object build from codeLaTeX and changing the occurrences of
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

    For most of methods, see the docstring of the corresponding method in LaTeXparser.CodeLaTeX
    """
    def __init__(self):
        self.codeLaTeX=LaTeXparser.CodeLaTeX("")
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
        self.codeLaTeX = LaTeXparser.CodeLaTeX(text)
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
        print "XML file is probably empty."
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

class Request(object):
    """ Contains what a lst_foo.py file has to contain """
    def __init__(self,name=None):
        #self.name = name           # I believe that does not serve anymore (May 12 2011)
        self.plugin_list = []
        self.original_filename = ""
        self.ok_filenames_list = []
        self.prerequiste_list = []
        self.fileTracking=FileTracking()
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

