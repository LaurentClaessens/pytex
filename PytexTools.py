# -*- coding: utf8 -*-

###########################################################################
#	This is part of the the package LaTeXparser
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
Contains tools (using LaTeXparser) intended to create good plugins for pytex.

pytex is a non-yet published pre-compilation system. Don't try to understand what this module serves to.
"""

import os
import hashlib
from xml.dom import minidom
import LaTeXparser

class Compilation(object):
	"""
	Launch the compilation of a document in various ways.
	Takes a filename as argument

	Usage examples
	X=LaTeXparser.Compilation("MyLaTeXFile.tex")	# Creates the Compilation object
	X.bibtex()					# Apply bibtex
	X.chain_dvi_ps_pdf()				# Produce the pdf file
	"""
	def __init__(self,filename):
		self.filename=filename
		self.generic_filename = self.filename[:self.filename.rindex(".")]
	def bibtex(self):
		commande_e="bibtex "+self.generic_filename
		os.system(commande_e)
	def makeindex(self):
		commande_e="makeindex "+self.generic_filename
		os.system(commande_e)
	def nomenclature(self):
		commande_e="makeindex -s nomencl.ist -o "+self.generic_filename+".nls "+self.generic_filename+".nlo"		
		os.system(commande_e)
	def special_stuffs(self):
		self.bibtex()
		self.makeindex()
		self.nomenclature()
	def latex(self):
		"""Produce a dvi file"""
		commande_e="/usr/bin/latex --src-specials "+self.filename
		os.system(commande_e)
	def chain_dvi_ps(self,papertype="a4"):
		"""
		The chain tex->div->ps

		After compiling by self.latex(), produce a ps file from the dvi by the command
		dvips -t <papertype> <self.filename>.dvi
		
		Optional parameter : papertype is "a4" by default
		"""
		self.latex()
		commande_e="dvips -t %s %s.dvi"%(papertype,self.generic_filename)
		os.system(commande_e)
	def chain_dvi_ps_pdf(self,papertype="a4"):
		"""
		The chain tex->dvi-ps->pdf 
		This is more or less the only way to produce a pdf file containing pstricsk figures and hyperref links.

		After having produced the ps by self.chain_dvi_ps(), produce a pdf file from the ps by the command
		ps2pdf <self.filename>.ps
		
		Optional parameter : papertype is "a4" by default (to be passed to dvips)
		"""
		self.chain_dvi_ps(papertype)
		commande_e="ps2pdf "+self.generic_filename+".ps" 
		os.system(commande_e)
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
	"""
	def __init__(self,name,tag):
		dict.__init__({})
		self.tag=tag
		self.name=name
		self.put_macro="\Put"+self.name
	def feed(self,xmlCode):
		r"""
		Read the code and fill the dictionary.
			Example
			xmlCode is parsed. Let consider the following lines :

				<CodeBox label="an example box">
				This is my \LaTeX\ code.
				</CodeBox>

			will add the code «This is my \LaTeX\ code» in the dictionary with the key «an example box»
		"""
		xmlCode_corrected=xmlCode.replace("&","[PytexSpecial amp]")
		dom = minidom.parseString(xmlCode_corrected)
		for box in dom.getElementsByTagName("CodeBox"):
			dict_name = box.getAttribute("dictName")
			if dict_name == self.name :
				label = box.getAttribute("label")
				pre_code = getText(box.childNodes)
				code = "\n".join(pre_code.split("\n")[1:-1])	# Because minidom adds an empty line at first and last position.
				self[label]=LaTeXparser.CodeLaTeX(code.replace("[PytexSpecial amp]","&"))
	def put(self,codeLaTeX):
		# This function is added to the plugin list of Request when using the method Request.create_magic_box
		r"""
		Substitute the dictionary inside codeLaTeX. 
			If we continue the example of the method CodeBox.feed, the line
			\put_mydict{mylabel}
			will be changed to
			This is my \LaTeX\ code.
		You can (this is the aim!) substitute the code at several places.

		return a new object LaTeXparser.CodeLaTeX
		"""
		A=codeLaTeX.copy()
		liste_occurrences = A.search_use_of_macro(self.put_macro,2)
		for occurrence in liste_occurrences :
			tags=occurrence.arguments[0].split(",")
			if tags == [""] or self.tag in tags :	# If we don't mention a tag, they are all good
				try :
					label=occurrence.arguments[1]
					B=self[label]
					B=self.put(B)			# This function is recursive !
					A=A.replace(occurrence.as_written,B.text_brut)
				except IndexError :
					print "PytexTools error : \Put... needs two arguments. Don't forget the tag"
					print occurrence.as_written
					raise
			else :
				A=A.replace(occurrence.as_written,"")
		return A

def FileToSha1sum(f):
	text = str(open(f).read())
	return hashlib.sha1(text).hexdigest()

ELEMENT_FOLLOWED_FILES = "Followed_files"
TAG_FICHIER="fichier"
class Request(object):
	""" Contains what a lst-foo.py file has to contain """
	def __init__(self):
		self.plugin_list = []
		self.original_filename = ""
		self.ok_filenames_list = []
		self.followed_files_list = []
		self.prerequiste_list = []
		self.xml_filename = "pytextools.xml"
	def create_magic_box(self,filename,boxname,tag):
		magic_box_code = LaTeXparser.FileToText(filename)
		self.magic_box = CodeBox(boxname,tag)
		self.magic_box.feed(magic_box_code)
		self.plugin_list.append(self.magic_box.put)
	def xml_record(self):
		return minidom.parse(self.xml_filename)
	def old_sha(self,f):
		""" Return the sha1 of f recorded in pytextools.xml """
		root = self.xml_record()
		fileNodes = root.getElementsByTagName(ELEMENT_FOLLOWED_FILES)
		for fileNode in fileNodes: 
			for fich in fileNode.getElementsByTagName(TAG_FICHIER):
				if fich.getAttribute("name")==f:
					return fich.getAttribute("sha1sum")
	def is_file_changed(self,f):
		sha_now = FileToSha1sum(f)
		if f not in self.followed_files_list :
			return True
		return not sha_now == self.old_sha(f)
	def follow_file(self,f):
		"""
		At the end of run_prerequistes, write the sha1 sum of the files in pytextools.xml
		"""
		self.followed_files_list.append(f)
	def xml(self):
		"""Return the xml code to be written in pytextools.xml"""
		followed_files_xml = minidom.Document()
		the_sha = followed_files_xml.createElement(ELEMENT_FOLLOWED_FILES)
		for f in self.followed_files_list :
			sha=FileToSha1sum(f)
			xml = followed_files_xml.createElement(TAG_FICHIER)
			xml.setAttribute('name',f)
			xml.setAttribute('sha1sum',sha)
			the_sha.appendChild(xml)
		followed_files_xml.appendChild(the_sha)
		return followed_files_xml.toprettyxml()
	def run_prerequistes(self,arg):
		for plug in self.prerequiste_list:
			plug(arg)
		open(self.xml_filename,"w").write(self.xml())

