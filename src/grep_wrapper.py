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

# copyright (c) Laurent Claessens, 2019
# email: laurent@claessens-donadello.eu


"""
This is a 'grep' adapted to our needs.
"""

import subprocess
from pathlib import Path
from src.Utilities import git_tracked_files

dprint = print

class PytexGrep():
    """
    This class serves to search for "label", "ref" and "eqref"
    in the git-tracked '.tex' files.

    Intended to be a singleton.
    """
    def __init__(self, dirname):
        self.dirname = dirname
        self.ref_dict = {}
        self.eqref_dict = {}
        self.label_dict = {}
        self._done_dict = False
    def create_lines_dict(self):
        """
        Create the dictionaries (filename, line number) -> string
        """
        for filename in git_tracked_files(Path.cwd()):
            if not filename.name.endswith('.tex'):
                continue
            ref_dict, eqref_dict, label_dict = self.read_file(filename)
            self.ref_dict = {**self.ref_dict, **ref_dict}
            self.eqref_dict = {**self.eqref_dict, **eqref_dict}
            self.label_dict = {**self.label_dict, **label_dict}
        self._done_dict = True
    def grep(self, command, label):
        """
        Make the search. 

        @param {string} `command`
            must be "ref", "eqref" or "label"
        @param {string} `label`
            The label to be searched

        ex:
        <myobject>.grep("eqref", "FOO")
        searches for \eqref{FOO}
        """
        if not self._done_dict:
            self.create_lines_dict()
        if command == "ref":
            line_dict = self.ref_dict
        if command == "eqref":
            line_dict = self.eqref_dict
        if command == "label":
            line_dict = self.label_dict
        string = "\\" + command + "{" + label + "}"
        for key, line in line_dict.items():
            if string in line:
                color_label = f"\033[35;37m{label}\033[35;33m"
                yield key, line.replace(label, color_label)
    def read_file(self, filename):
        """
        Read the given file and add its lines in `self`'s 
        line dictionary.

        @return {tuple of dictionaries}
            - ref dictionary
            - eqref dictionary
            - label dictionary
        """
        local_ref_dict = {}
        local_eqref_dict = {}
        local_label_dict = {}
        with open(filename, 'r') as tex_file:
            number = 0
            for line in tex_file.readlines():
                number += 1
                if "\\ref{" in line:
                    local_ref_dict[(filename, number)] = line
                if "\eqref{" in line:
                    local_eqref_dict[(filename, number)] = line
                if "\label{" in line:
                    local_label_dict[(filename, number)] = line
        return local_ref_dict, local_eqref_dict, local_label_dict
                
                
    def is_correct_line(self, line):
        """
        Say if a line is interesting or not four our "grep" purpose.
        To be interesting, the line must contain "\ref", "\eqref" 
        or "\label"
        """
        if "\eqref{" in line:
            return True
        if "\\ref{" in line:
            return True
        if "\label{" in line:
            return True
        return False
