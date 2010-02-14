# -*- coding: utf8 -*-

###########################################################################
#	This is part of the module phystricks
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
# email: laurent.claessens@uclouvain.be

"""
This is a very basic LaTeX parser intended to be used within phystricks.
"""

paires = { "{":"}","[":"]" }
accepted_between_arguments = ["%","\n"," ","	"] # the last one is a TAB
definition_commands = [ "\\newcommand","\\renewcommand" ]	# In the method dict_of_definition_macros, I hard-code the fact that 
								# these definition commands have 3 arguments.

def compactization(text,accepted_between_arguments):		
	for acc in accepted_between_arguments :
		text=text.replace(acc,"")
	return text

def SearchFitBrace(text,position,open):
	"""
	return a tuple containing the text withing the next pair of open/close brace and the position where the pair closes in text

	Consider the string 
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
	def __init__(self,name,arguments,as_written=""):
		self.arguments = arguments
		self.number_of_arguments = len(arguments)
		self.name = name
		self.as_written = as_written

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
		#print "I have the impression that %s has %s arguments"%(name,number_of_arguments)
	use = []

	while position != -1 :
		# We don't want to fit the place where the name is defined. Thus we test if it is preceded by
		# \newcommand or \renewcommand
		test_newcommand = "\\"+compactization(remaining_text[:position],accepted_between_arguments).split("\\")[-1]
		remaining_text = remaining_text[position+len(name):]
		if test_newcommand not in [defs+"{" for defs in definition_commands]:
			remaining = remaining_text
			arguments, as_written = SearchArguments(remaining,number_of_arguments)
			as_written = name+as_written
			use.append(Occurrence(name,arguments,as_written))
		position = remaining_text.find(name)
	return use
	

def MacroDefinition(code,name):
	"""
	Finds the (last) definition of a macro and returns the corresponding object

	text : the text (a LaTeX source file) where we are searching in
	name : the name of the macro we want to analyse

	We search for the definition under one of the two forms
	\newcommand{\name}[n]{definitio}
	\newcommand{\name}{definitio}

	A crash is probably raised if the macro is not defined in the text :(
	"""
	#print "Je recherche la définition de ",name
	#for definer in definition_commands :
	#	for newcommand in [Occurrence_newcommand(a) for a in [SearchUseOfMacro(text,definer,3) for definer in definition_commands]]:
	#		print "J'ai trouvé la définition de ",newcommand.name
	#		if newcommand.name == name :
	#			 found = newcommand
	#return found
	if type(code) == CodeLaTeX :
		return code.dict_of_definition_macros()[name]
	else :
		print "Je recrée, mais ce n'est pas supposé arriver."
		return CodeLaTeX(code).dict_of_definition_macros()[name]

class Occurrence_newlabel(object):
	"""
	takes an occurrence of \\newlabel and creates an object which contains the information.
	"""
	def __init__(self,occurrence):
		self.occurrence = occurrence
		self.arguments = self.occurrence.arguments
		if len(self.arguments) == 0 :
			self.name = "Non interesting; probably the definition"
			self.listoche = [None,None,None,None,None]
		else :
			self.name = self.arguments[0][0]
			self.listoche = [a[0] for a in SearchArguments(self.arguments[1][0],5)]
		self.value = self.listoche[0]
		self.page = self.listoche[1]
		self.section_name = self.listoche[2]
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

class CodeLaTeX(object):
	""" Contains the informations about a tex file """
	def __init__(self,text_brut):
		"""
		self.text_brut	contains the tex code as given
		self.text 	contains the tex code from which one removed the comments.
		"""
		self.text_brut = text_brut
		self.text_without_comments = RemoveComments(self.text_brut)
		self._dict_of_definition_macros = {}
		self._list_of_input_files = []
	def search_use_of_macro(self,name,number_of_arguments=None):
		return SearchUseOfMacro(self,name,number_of_arguments)
	def macro_definition(self,name):
		return MacroDefinition(self,name)
	def statistics_of_the_macro(self,name):
		return StatisticsOfTheMacro(self,name)
	def dict_of_definition_macros(self):
		"""
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

	def substitute_input(self,filename,text):
		""" 
		replace \input{...} by the text 

		This function is recursive but I pity the fool who makes recursion in his LaTeX document.
		"""
		list = []
		for occurrence in self.search_use_of_macro("\input",1):
			x = occurrence.analyse()
			if x.filename == filename :
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
