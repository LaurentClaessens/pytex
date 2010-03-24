#! /usr/bin/python
# -*- coding: utf8 -*-

import LaTeXparser

def use_of_newlabel(filename):
	"""
	For each label, gives some details : name, value, page, section name
	"""
	codeLaTeX =  LaTeXparser.FileToCodeLaTeX(filename+".aux")
	for newlabel in codeLaTeX.analyse_use_of_macro("\\newlabel",2) :
		print "+++"
		print "name :",newlabel.name
		print "value : ",newlabel.value
		print "page : ",newlabel.page
		print "section name : ",newlabel.section_name


def use_of_macros(filename):
	"""
	For each defined macro, says how many times it was used.
	"""
	codeLaTeX =  LaTeXparser.FileToCodeLaTeX(filename+".tex")
	for name in liste:
		num = codeLaTeX.statistics_of_the_macro(name).number_of_use
		print "La macro %s est utilisée %s fois"%(name,str(num))

def text_of_macro(filename, macro):
	"""
	Gives the text as appears when the given macro is used.
	"""
	codeLaTeX =  LaTeXparser.FileToCodeLaTeX(filename+".tex")
	for occurrence in codeLaTeX.search_use_of_macro("\MyMacro",2):
		print occurrence.as_written

def use_of_input(filename):
	"""
	Writes the files that are in \input{}. Does not add .tex if missing

	Notice that the list can be directly obtained by the shortcut
	codeLaTeX.list_of_input_files()
	"""
	f = manip.Fichier(filename+".tex")
	codeLaTeX =  LaTeXparser.CodeLaTeX(f.texte())
	x = codeLaTeX.search_use_of_macro("\\input",1)
	for occurrence in x :
		input = occurrence.analyse()
		print input.filename

def remove_comments(filename):
	""" 
	print the given file with no comments.
	It does not remove the % symbol, since it is sometimes written by purpose.
	"""
	codeLaTeX =  LaTeXparser.FileToCodeLaTeX(filename+".tex")
	x = codeLaTeX.remove_comments()
	print x.text_brut
	print x.text_brut == x.remove_comments().text_brut		# should print "True"

def substitute_input(filename,inputname,text=None):
	"""
	substitute the \input{inputname} by the given text.
	"""
	codeLaTeX =  LaTeXparser.FileToCodeLaTeX(filename+".tex")
	print codeLaTeX.list_of_input_files()
	recode = codeLaTeX.substitute_input(inputname,text)
	print recode.text_brut

def test_all():
	use_of_newlabel("ess_big")
	use_of_macros("ess_big")
	use_of_input("ess_big")
	text_of_macro("ess","\MyMacro")
	remove_comments("ess")
	use_of_newlabel("ess_big")
	# Return the file as string with the text instead of \input{fichier}
	substitute_input("ess","fichier","HERE WAS AN INPUT OF THE FILE ess")	
	# Return the file as string with the content of fichier.tex instead of \input{fichier}
	substitute_input("ess","fichier")				


#test_all()		# Uncomment if you want to test everything.
use_of_macros("ess")
