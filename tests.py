#! /usr/bin/python
# -*- coding: utf8 -*-

import LaTeXparser
import LaTeXparser.PytexTools
from xml.dom import minidom

def getText(nodelist):
	rc = ""
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc = rc + node.data
	return rc

def xml_read():
	dom = minidom.parse("magical_box.tex")
	for box in dom.getElementsByTagName("CodeBox"):
		print box.getAttribute("label")
		text = getText(box.childNodes)
		print "\n".join(text.split("\n")[1:-1])	# Because minidom adds an empty line at first and last position.

def follow_the_file():
	myRequest = LaTeXparser.PytexTools.Request()
	myRequest.follow_file("ess.py")
	myRequest.follow_file("ess.aux")
	myRequest.run_prerequistes("XXX")

#follow_the_file()
xml_read()
