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

# copyright (c) Laurent Claessens, 2010,2012-2016, 2019-2020
# email: laurent@claessens-donadello.eu

"""Expose a class to manipulate/read a LaTeX log file."""


from src.Warnings import ReferenceWarning
from src.Warnings import MultiplyLabelWarning
from src.Warnings import CitationWarning
from src.Warnings import LabelWarning
from src.Warnings import OverfullWarning
from src.Warnings import TeXCapacityExceededWarning
from src.utilities import IndentPrint
from src.utilities import is_empty_line

dprint = print      # pylint: disable=invalid-name


class LogCode:
    """
    Contains informations about log file.

    If your code is in a file, please use the function
    FileToLatexCode :
    FileToLogCode("MyFile.log")
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, text_brut, options, filename=None, stop_on_first=False):
        """
        Initialize.

        self.text_brut          contains the tex code as given
        """
        self.options = options
        self.text_brut = text_brut
        self.filename = filename
        self.undefined_references = []
        self.undefined_citations = []
        self.undefined_labels = []
        self.multiply_labels = []
        self.stop_on_first = stop_on_first
        self._rerun_to_get_cross_references = None
        self.warnings = None
        self.maybe_more = "LaTeX Warning: Label(s) may have "\
                          "changed. Rerun to get cross-references right."

        self.search_for_errors(stop_on_first=self.stop_on_first)

    def rerun_to_get_cross_references(self, stop_on_first=False):
        """Re-run the compilation to get the cross-references right."""
        if self._rerun_to_get_cross_references is None:
            self.search_for_errors(stop_on_first=stop_on_first)
        return self._rerun_to_get_cross_references

    def search_for_still_cross_references(self):
        """Search if there are still wrong cross-references."""
        return self.maybe_more in self.text_brut

    def search_for_errors(self, stop_on_first=False):
        """Search for errors."""
        # pylint: disable=too-many-branches
        still_cross_references = self.search_for_still_cross_references()
        self._rerun_to_get_cross_references = False
        if stop_on_first:
            if still_cross_references:
                self._rerun_to_get_cross_references = True
        if self._rerun_to_get_cross_references:
            return None

        print("Analysing log file", self.filename)
        warnings = self.text_brut.split("Warning: ")
        for warning in warnings[1:]:
            text = warning[0:warning.find(".")]
            mots = text.split(" ")
            genre = mots[0]
            label = mots[1][1:-1]
            try:
                dprint("mots", mots)
                page = mots[mots.index("page")+1]
            except ValueError:
                page = -1
            except IndexError:
                # There is a warning 
                # "I moved some lines to the next page."
                continue
            if genre == "Reference":
                labels = [w.label
                          for w in self.undefined_references]
                if label not in labels:
                    self.undefined_references.append(
                        ReferenceWarning(label,
                                         page,
                                         self.options))
            if genre == "Label":
                if label not in [w.label for w in self.undefined_labels]:
                    self.multiply_labels.append(
                        MultiplyLabelWarning(label,
                                             page,
                                             self.options))
            if genre == "Citation":
                undef_labels = [w.label
                                for w in self.undefined_citations]
                if label not in undef_labels:
                    warning = CitationWarning(label,
                                              page,
                                              self.options)
                    self.undefined_citations.append(warning)

        self.warnings = []
        self.warnings.extend(self.undefined_references)
        self.warnings.extend(self.undefined_citations)
        self.warnings.extend(self.multiply_labels)

        if still_cross_references:
            self.warnings.append(LabelWarning(self.maybe_more))
            self._rerun_to_get_cross_references = True
        else:
            self._rerun_to_get_cross_references = False

        with IndentPrint("Search for the Overfull hbox"):
            self.check_overfull_hbox()

        self.check_tex_capacity_exeeded()
        self.probs_number = len(self.warnings)

        return None

    def check_overfull_hbox(self):
        r"""
        Check if there are Overful hbox.

        For each of them, we will display the line with 'Overfull \hbox'
        and the following lines up to the next empty line.
        """
        search = "Overfull"
        in_overfull = False
        in_bbl = False
        overfull_lines = []
        file_lines = []
        for line in self.text_brut.splitlines():
            if ".tex" in line:
                in_bbl = False
                file_lines = [line]
            if ".bbl" in line:
                in_bbl = True
                file_lines = [line]
            if '[' in line or "]" in line:
                file_lines.append(line)
            if in_bbl:
                in_overfull = False
            if in_overfull:
                overfull_lines.append(line)
                if is_empty_line(line):
                    in_overfull = False
                    text = "\n".join(file_lines)
                    text = text + "\n".join(overfull_lines)
                    self.warnings.append(OverfullWarning(text))
                    with IndentPrint("One overfull hbox"):
                        print(text)
                    overfull_lines = []
                    file_lines = []
            if search in line:
                if not in_bbl:
                    overfull_lines.append(line)
                    in_overfull = True

    def check_tex_capacity_exeeded(self):
        """Check for 'tex capacity exeeded'."""
        search = "TeX capacity exceeded"
        if search in self.text_brut:
            self.warnings.append(TeXCapacityExceededWarning(search))

    def remove_duplicate_warnings(self):
        """Remove the duplicate warnings."""
        labels = []
        new_warns = []
        for warn in self.warnings:
            if warn.label not in labels:
                new_warns.append(warn)
                labels.append(warn.label)
        self.warnings = new_warns

    def __str__(self):
        """Return a summary of the problems."""
        answer = []

        self.remove_duplicate_warnings()

        for warn in self.warnings:
            with IndentPrint("One warning"):
                answer.append(warn.__str__())
        if self.probs_number > 1:
            answer.append("Il reste encore %s problèmes à régler. Bon travail." %
                          str(self.probs_number))
        if self.probs_number == 1:
            answer.append(
                "C'est ton dernier problème à régler. Encore un peu de courage !")

        return "\n".join(answer)
