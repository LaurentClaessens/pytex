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

# TODO : this function is buggy when fast=True
def LatexCodeToRoughSource(codeLaTeX,filename,bibliography_bbl_filename=None,index_ind_filename=None,fast=False):
    """
    Return a file containing rough self-contained sources that are ready for upload to Arxiv.
    What it does
        1. Perform all the \input recursively
        2. Remove the commented lines (leave the % symbol itself)
        3. Include the bibliography, include .bbl file (no bibtex needed)
        4. Include the index, include .ind file (no makeindex needed)
    What is does not
        1. Check for pdflatex compliance. 

    Input 
        codeLaTeX : an object of type LatexCode
        filename : the name of the file in which the new code will be written
    Optional
        bibliography_bbl_filename : the name of the .bbl file. If not give, will be guesse by changing ".tex"->".bbl" in codeLaTeX.filename
        index_ind_filename :        the name of the .bbl file. If not give, will be guesse by changing ".tex"->".ind" in codeLaTeX.filename
    Output
        Create the file named <filename>
        return the new code as LatexCode

    The result is extremely hard-coded. One has not to understand it as a workable LaTeX source file.
    """
    from src.all import FileToLatexCode
    if not bibliography_bbl_filename :
        bibliography_bbl_filename = codeLaTeX.filename.replace(".tex",".bbl")
    if not index_ind_filename :
        index_ind_filename = codeLaTeX.filename.replace(".tex",".ind")
    print("Creating bibliography")
    code_biblio = FileToLatexCode(bibliography_bbl_filename)
    print("Creating index")
    code_index = FileToLatexCode(index_ind_filename)

    new_code = codeLaTeX.copy()
    new_code=new_code.substitute_all_inputs(fast=fast)
    resultBib = re.search("\\\\bibliography\{.*\}",new_code.text_brut)
    if resultBib != None :
        ligne_biblio = resultBib.group()
        new_code = new_code.replace(ligne_biblio,code_biblio.text_brut)

    printindex=re.escape("\printindex")
    resultIndex = re.search(printindex,new_code.text_brut)

    if resultIndex != None :
        new_code = new_code.replace(printindex,code_index.text_brut)
    new_code.filename = filename
    new_code.save()
    return new_code
