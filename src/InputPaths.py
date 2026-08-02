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

# copyright (c) Laurent Claessens, 2016-2017, 2019, 2026
# email: laurent@claessens-donadello.eu

from pathlib import Path



class InputPaths(object):
    """
    This object recall the list of paths in which \input will search for its files.
    """

    def __init__(self):
        self.directory_list:list[Path] = [Path(".").resolve()]

    def append(self, dirname:Path):
        assert isinstance(dirname, Path)
        self.directory_list.append(dirname)

    def get_file(self, filename:str):
        """
        - `filename` : a file name like "foo.tex"

        Search in the subdirectories for a `foo.tex`
        and return the first found.
        """
        for directory in self.directory_list:
            filepath = directory / filename
            if filepath.is_file():
                return filepath
        raise NameError("No file found with name ", filename)

    def __str__(self):
        return str(self.directory_list)

    def __iter__(self):
        return iter(self.directory_list)
