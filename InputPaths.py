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

# copyright (c) Laurent Claessens, 2016
# email: laurent@claessens-donadello.eu

import os.path

class InputPaths(object):
    """
    This object recall the list of paths in which \input will search for its files.
    """
    def __init__(self):
        self.directory_list=["."]
    def append(self,dirname):
        self.directory_list.append(dirname)
    def get_file(self,filename):
        """
        - `filename` : a file name like "foo.tex"

        Search in the subdirectories for a `foo.tex` and return the first found.
        """
        for directory in self.directory_list :
            fn=os.path.join(directory,filename)
            if os.path.exists(fn):
                return fn
        raise NameError("No file found with name ",filename)

