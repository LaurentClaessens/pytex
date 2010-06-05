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

import LaTeXparser

class CodeBox(dict):
	"""
	This class is intended to keep some portions of LaTeX code in a fresh box, allowing to retrieve them later.
	"""
	def __init__(self,name):
		dict.__init__({})
		self.name=name
		self.feed_macro="\\Feed"+self.name
		self.put_macro="\Put"+self.name
	def feed(self,codeLaTeX):
		r"""
		Read the code and fill the dictionary.
			Example
			If self.name is "mydict", codeLaTeX is parsed. Let consider the following line :

			\feed_mydict{thislabel}{This is my \LaTeX\ code}

			will add the code «This is my \LaTeX\ code» in the dictionary with the key «thislabel»
		"""
		liste_occurrences = codeLaTeX.search_use_of_macro(self.feed_macro,2)
		for occurrence in liste_occurrences :
			label = occurrence.arguments[0]
			code = LaTeXparser.CodeLaTeX(occurrence.arguments[1])
			self[label]=code
	def put(self,codeLaTeX):
		r"""
		Substitute the dictionary inside codeLaTeX. 
			If we continue the example of the method self.feed, the line
			\put_mydict{mylabel}
			will be changed to
			This is my \LaTeX\ code.
		You can (this is the aim!) substitute the code at several places.

		return a new object LaTeXparser.CodeLaTeX
		"""
		A=codeLaTeX.copy()
		liste_occurrences = A.search_use_of_macro(self.put_macro,1)
		for occurrence in liste_occurrences :
			label=occurrence.arguments[0]
			A=A.replace(occurrence.as_written,self[label].text_brut)
		return A

class Request(object):
	""" Contains what a lst-foo.py file has to contain """
	def __init__(self):
		self.plugin_list = []
		self.original_filename = ""
		self.ok_filenames_list = []
		self.prerequiste=[]
	def create_magic_box(self,filename,boxname):
		magic_box_code = LaTeXparser.FileToCodeLaTeX(filename)
		self.magic_box = CodeBox(boxname)
		self.magic_box.feed(magic_box_code)
		self.plugin_list.append(self.magic_box.put)
	def run_prerequistes(self,*arg,**args):
		for plug in self.prerequiste:
			plug
