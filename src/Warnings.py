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


class LaTeXWarning:
    def __init__(self, label, page, options):
        self.label = label
        self.page = page
        self.options = options

    def grep_result(self):
        a = []
        for command in ["ref", "eqref", "label"]:
            for key, line in self.options.grep(command, self.label):
                filename = key[0].name
                line_number = key[1]
                a.append(f"{filename}, {line_number}: {line}")
                a.append('')
        return "\n".join(a)


class OverfullWarning:
    """A warning about an Overfull hbox."""
    def __init__(self, text):
        """Initialize with the text."""
        self.text = text
        self.label = None

    def __str__(self):
        """Return the message to be displayed."""
        return self.text
        


class ReferenceWarning(LaTeXWarning):
    def __init__(self, label, page, options):
        LaTeXWarning.__init__(self, label, page, options)

    def __str__(self):
        # +"\n"
        return "\033[35;33m------ Undefined reference \033[35;37m {0} \033[35;33m à la page\033[35;33m {1} \033[35;33m------".format(self.label, self.page)+"\n"+self.grep_result()


class CitationWarning(LaTeXWarning):
    def __init__(self, label, page, options):
        LaTeXWarning.__init__(self, label, page, options)

    def __str__(self):
        return "\033[35;33m------ Undefined citation \033[35;37m %s \033[35;33m à la page\033[35;33m %s \033[35;33m------" % (self.label, str(self.page))+"\n"+self.grep_result()


class MultiplyLabelWarning(LaTeXWarning):
    def __init__(self, label, page, options):
        LaTeXWarning.__init__(self, label, page, options)

    def __str__(self):
        # +"\n"
        return "\033[35;33m------ \033[35;33m Multiply defined label \033[35;33m %s --------- " % self.label+"\n"+self.grep_result()


class TeXCapacityExceededWarning(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "\033[35;34m This is a serious problem : {0} ".format(self.text)


class LabelWarning(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "\033[35;32m {0} ".format(self.text)
