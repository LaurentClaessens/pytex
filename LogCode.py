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

# copyright (c) Laurent Claessens, 2010,2012-2016
# email: laurent@claessens-donadello.eu


from latexparser.Warnings import ReferenceWarning
from latexparser.Warnings import MultiplyLabelWarning
from latexparser.Warnings import CitationWarning
from latexparser.Warnings import LabelWarning

class LogCode(object):
    """
    Contains informations about log file.

    If your code is in a file, please use the function FileToLatexCode :
    FileToLogCode("MyFile.log")
    """
    def __init__(self,text_brut,filename=None,stop_on_first=False):
        """
        self.text_brut          contains the tex code as given
        """
        self.text_brut = text_brut
        self.filename = filename
        self.undefined_references=[]
        self.undefined_citations=[]
        self.undefined_labels=[]
        self.multiply_labels=[]
        self.stop_on_first=stop_on_first
        self.search_for_errors(stop_on_first=self.stop_on_first)
        self._rerun_to_get_cross_references=None
    def rerun_to_get_cross_references(self,stop_on_first=False):
        if self._rerun_to_get_cross_references == None:
            self.search_for_errors(stop_on_first=stop_on_first)
        return self._rerun_to_get_cross_references
    def search_for_still_cross_references(self):
        self.maybeMore ="LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
        return self.maybeMore in self.text_brut
    def search_for_errors(self,stop_on_first=False):
        still_cross_references=self.search_for_still_cross_references()
        self._rerun_to_get_cross_references = False
        if stop_on_first :
            if  still_cross_references :
                self._rerun_to_get_cross_references = True
        if not self._rerun_to_get_cross_references :
            print("Analysing log file",self.filename)
            Warns = self.text_brut.split("Warning: ")
            for warn in Warns[1:]:
                try :
                    text = warn[0:warn.find(".")]
                    mots=text.split(" ")
                    genre = mots[0]
                    label = mots[1][1:-1]
                    try :
                        page = mots[mots.index("page")+1]
                    except ValueError :
                        page = -1
                    if genre == "Reference" :
                        if label not in [w.label for w in self.undefined_references]:
                            self.undefined_references.append(ReferenceWarning(label,page))
                    if genre == "Label" :
                        if label not in [w.label for w in self.undefined_labels]:
                            self.multiply_labels.append(MultiplyLabelWarning(label,page))
                    if genre == "Citation" :
                        if label not in [w.label for w in self.undefined_citations]:
                            self.undefined_citations.append(CitationWarning(label,page))
                except ValueError :
                    pass
            self.warnings = []
            self.warnings.extend(self.undefined_references)
            self.warnings.extend(self.undefined_citations)
            self.warnings.extend(self.multiply_labels)

            if still_cross_references:
                self.warnings.append(LabelWarning(self.maybeMore))
                self._rerun_to_get_cross_references=True
            else :
                self._rerun_to_get_cross_references=False

            self.TeXcapacityexeeded="TeX capacity exceeded"
            if self.TeXcapacityexeeded in self.text_brut:
                self.warnings.append(TeXCapacityExceededWarning(self.TeXcapacityexeeded))

            self.probs_number=len(self.warnings)
    def tex_capacity_exeeded(self):
        return self.TeXcapacityexeeded in self.text_brut
    def __str__(self):
        a=[]
        for warn in self.warnings :
            a.append(warn.__str__())
        if self.probs_number > 1:
            a.append("Il reste encore %s problèmes à régler. Bon travail."%str(self.probs_number))
        if self.probs_number == 1:
            a.append("C'est ton dernier problème à régler. Encore un peu de courage !")
        return "\n".join(a)
    def __unicode__(self):
        raise DeprecationWarning
        return self.__unicode__().encode("utf8")

def ListOfCitation(filelist):
    r"""
    From a list of files, return the list of arguments in \cite{...}.
    """
    l=[]
    new_filelist=[a+".tex" for a in filelist]
    for f in new_filelist :
        codeLaTeX =FileToLatexCode(f)
        occurences = codeLaTeX.analyse_use_of_macro("\cite",1)
        for occ in occurences :
            l.append(occ.label)
    return l
