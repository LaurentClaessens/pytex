# -*- coding: utf8 -*-

###########################################################################
#	This is LaTeXparser.py
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

import os		# For the compilations.

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

paires = { "{":"}","[":"]" }
accepted_between_arguments = ["%","\n"," ","	"] # the last one is a TAB
definition_commands = [ "\\newcommand","\\renewcommand" ]	# In the method dict_of_definition_macros, I hard-code the fact that 
								# these definition commands have 3 arguments.
def FileToCodeLaTeX(name):
	""" return a codeLaTeX from a file """
	list_content = list(open(name,"r"))
	return CodeLaTeX("".join(list_content),filename=name)

def compactization(text,accepted_between_arguments):		
	for acc in accepted_between_arguments :
		text=text.replace(acc,"")
	return text

def SearchFitBrace(text,position,open):
	"""
	return a tuple containing the text withing the next pair of open/close brace and the position where the pair closes in text

	As an example, consider the string 
	s="Hello (Louis) how are you ?"
	SearchFitBrace(s,4,[" (",")"])
	returns ('Louis', 6, 12)
	because the next brace begins at position 6, finishes at position 12 and the text within in "Louis"
	"""
	close = paires[open]
	level = 0
	giventext = text[position:]
	startPosition = position+giventext.find(open)
	for i in range(startPosition,len(text)):
		if text[i] == open :
			level = level+1
		if text[i] == close :
			level = level-1
		if level == 0:
			return text[startPosition+1:i],startPosition,i

class Occurrence(object):
	"""
	self.as_written : the code as it appears in the file, including \MyMacro, including the backslash.
	"""
	def __init__(self,name,arguments,as_written=""):
		self.arguments = arguments
		self.number_of_arguments = len(arguments)
		self.name = name
		self.as_written = as_written
		self.arguments_list = [ a[0] for a in self.arguments ]
	def analyse(self):
		return globals()["Occurrence_"+self.name[1:]](self)		# We have to remove the initial "\" in the name of the macro.
	def __getitem__(self,a):
		return self.arguments[a]
	def __str__(self):
		return str(self.arguments)

def SearchArguments(remaining,number_of_arguments):
	"""
	From a string of the form {A}{B}{C}, returns the list ["A","B","C"].
	"""
	next_can_be_open = compactization(remaining,accepted_between_arguments)[0] 
	still_to_be_done = True
	arguments = []
	as_written = ""		# We will put in that variable the precise text that appears
	while (next_can_be_open in paires.keys()) and (still_to_be_done == True) and (len(arguments) < number_of_arguments) :
		arg,start,end = SearchFitBrace(remaining,0,next_can_be_open)
		as_written = as_written + remaining[:end]+"}"
		arguments.append((arg,next_can_be_open+paires[next_can_be_open]))
		remaining = remaining[end+1:]
		compact = compactization(remaining,accepted_between_arguments)
		if len(compact) >= 1:
			next_can_be_open = compact[0]
		else :
			still_to_be_done = False
			# If we have \MyMacro{foo}\MyMacro{bar}, at the end of the parsing of the first,
			# remaining is empty. Thus the search of new arguments ceases when the remaining is empty 
			# (the condition still_to_be_done) or when the remaining does not begin by an opening brace
			# (the condion next_can_be_open).
	return arguments, as_written

def SearchUseOfMacro(code,name,number_of_arguments=None):
	"""
	number_of_arguments is the number of arguments expected. 
				Giving a too large number produces wrong results in the following example case where \MyMacro
				is supposed to have 3 arguments :
				\MyMacro{A}{B}{C}
				{\\bf An other text}
				The {\\bf ...} group is not a parameter of \MyMacro, while it will be fitted as a parameter.
			It None is given, we search first for the definition and then the expected number of arguments is deduced.

			Notice that the number_of_arguments is supposed to be the number of non optional arguments. We do not count the arguments
			within [] in the number.
	We do not fit the macros that are used in the comments.
	"""
	text = code.text_without_comments
	remaining_text = text
	position  = remaining_text.find(name)
	starting_position = position

	if number_of_arguments == None :
		number_of_arguments = code.dict_of_definition_macros()[name].number_of_arguments
	use = []

	while position != -1 :
		# We don't want to fit the place where the name is defined. Thus we test if it is preceded by
		# \newcommand or \renewcommand
		test_newcommand = "\\"+compactization(remaining_text[:position],accepted_between_arguments).split("\\")[-1]
		remaining_text = remaining_text[position+len(name):]
		if test_newcommand not in [defs+"{" for defs in definition_commands]:
			remaining = remaining_text
			arguments, as_written = SearchArguments(remaining,number_of_arguments)
			as_written = "\\"+name+as_written
			use.append(Occurrence(name,arguments,as_written))
		position = remaining_text.find(name)
	return use
	

def MacroDefinition(code,name):
	r"""
	Finds the (last) definition of a macro and returns the corresponding object

	text : the text (a LaTeX source file) where we are searching in
	name : the name of the macro we want to analyse

	We search for the definition under one of the two forms
	\newcommand{\name}[n]{definitio}
	\newcommand{\name}{definitio}

	A crash is probably raised if the macro is not defined in the text :(
	"""
	if type(code) == CodeLaTeX :
		return code.dict_of_definition_macros()[name]
	else :
		print "Je recrée, mais ce n'est pas supposé arriver."
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
			self.fourth = self.listoche[3]		# I don't know the role of the fourth argument
			self.fifth = self.listoche[4]		# I don't know the role of the fifth argument

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
		self.filename = self.occurrence[0][0]

class Occurrence_MyMacro(object):
	def __init__(self,arguments):
		self.arguments = arguments
		print "J'ai repréré le premier argument ",arguments[0]

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
		line_withoutPC.append(ligne+"\n")
	code_withoutPC = "".join(line_withoutPC)

	final_code = code_withoutPC
	# Now we remove what is after \end{document}
	if "\end{document}" in final_code :
		final_code = code_withoutPC.split("\end{document}")[0]+"\end{document}"
	return final_code

class newlabelNotFound(object):
	"""Exception class for CodeLaTeX.get_newlabel_value"""
	def __init__(self,label_name):
		self.label_name = label_name

class CodeLaTeX(object):
	""" Contains the informations about a tex file """
	def __init__(self,text_brut,filename=None):
		"""
		self.text_brut			contains the tex code as given
		self.text_without_comments 	contains the tex code from which one removed the comments.
		"""
		self.text_brut = text_brut
		self.text_without_comments = RemoveComments(self.text_brut)
		self._dict_of_definition_macros = {}
		self._list_of_input_files = []
		self.filename = filename
	def save(self,filename=None):
		"""
		Save the code in a file. The optional argument provides a file name that overrides the self.filename. If none of filename and self.filename are give, an exception is raised.
		"""
		if not filename :
			filename = self.filename
		f = open(filename,"w")
		f.write(self.text_brut)
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
		

	def search_use_of_macro(self,name,number_of_arguments=None):
		"""
		Return a list of Occurrence of a given macro

		Optional argument: number_of_arguments=None
		"""
		return SearchUseOfMacro(self,name,number_of_arguments)
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
		replace \input{...} by the text.

		By default, it replaces by the content of <filename> (add .tex if no extension is given) which is taken in the current directory.

		Some remarks
		1. This function is recursive but I pity the fool who makes recursion in his LaTeX document.
		2. It does not really check the context. A \input in a verbatim environment will be replaced !
		3. If a file is not found, a warning is printed and no replacement are done.
		"""
		list = []
		if text==None:
			strict_filename = filename
			if "." not in filename:
				strict_filename=filename+".tex"
			try:
				text = "".join( open(strict_filename,"r") )
			except IOError :
				print "Warning : file «%s» not found. No replacement done."%strict_filename
				return self
		for occurrence in self.search_use_of_macro("\input",1):
			x = occurrence.analyse()
			if x.filename == filename :			# Create the list of all the texts of the form \input{<filename>}
				list.append(x.occurrence.as_written)
		A = CodeLaTeX(self.text_brut)
		for as_written in list :
			A = A.replace(as_written,text)
		return A
	def remove_comments(self):
		return CodeLaTeX(self.text_without_comments)
	def find(self,arg):
		return self.text.find(arg)
	def replace(self,textA,textB):
		"""
		Replaces textA by textB in self.text_brut, but without performing the replacement in the comments.
		"""
		lines = self.text_brut.split("\n")
		new_text = ""
		for line in lines :
			placePC = line.find("%")
			if placePC == -1:
				new_line = line.replace(textA,textB)+"\n"
			else:
				new_line = line[:placePC+1].replace(textA,textB)+line[placePC+1:]+"\n"
			new_text = new_text + new_line
			#print line
			#print "->"
			#print new_line
		return CodeLaTeX(new_text)
