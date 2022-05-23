###########################################################################
#   This is part of the module phystricks
#
#   phystricks is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   phystricks is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with phystricks.py.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# copyright (c) Laurent Claessens, 2010-2017, 2019
# email: laurent@claessens-donadello.eu

import re
import os
import sys
import codecs
import subprocess
from pathlib import Path
import time
import datetime
import json
import random
import string
import hashlib

LOGGING_FILENAME = ".pytex.log"

dprint = print

# If one moves the class 'ReferenceNotFoundException', one has to update the message in pytex.


class IndentPrint:
    """Furnish a context manager for indenting the print."""

    def __init__(self, title):
        """Initialize with the title."""
        self.title = title
        self.old_stdout = None

    def write(self, text):
        """Print the given text with an indentation."""
        self.old_stdout.write(f"  {text}")

    def __enter__(self):
        """Print the title before to initiate the indentations."""
        self.old_stdout = sys.stdout
        self.old_stdout.write(self.title + '\n')
        sys.stdout = self

    def __exit__(self, *arrgs):
        """Give back the stdout."""
        sys.stdout = self.old_stdout


def git_tracked_files(dirname):
    """
    Yield the files that are git-tracked

    @param {string or PosixPath}
    """

    # I know there are git modules for Python, but I want to
    # have no dependencies since 'pytex' is already an heavy
    # dependency for Frido.
    git_dir = Path(dirname)
    old_dir = Path.cwd()
    os.chdir(git_dir)

    bash_command = "git ls-tree --name-only -r HEAD"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    os.chdir(old_dir)
    output, error = process.communicate()
    output = output.decode('utf8')

    for filename in output.split("\n"):
        if os.path.isfile(filename):
            yield git_dir / filename


def is_empty_line(line):
    """Say if the given line is an empty line."""
    if not line.strip():
        return True
    return False


class ReferenceNotFoundException(Exception):
    """
    Exception raised when pytex is not able to find back the
    fautive \\ref causing a future reference.

    EXPLANATION

    In order to detect the future references, pytex creates a big
    latex document (in memory) that recursively contains all the \input.
    This is more or less a single self-contained file equivalent
    to the given file.

    When a future reference is found in that document, we search back
    the line in the real files in order to provide the user an
    instructive message (filename+line number)

    Suppose that we have
    \input{foo}     % this is a comment
    and that the last line of 'foo.tex' contains the fautive \\ref :
    "using theorem \ref{LAB}, blah"

    In that case, the processus of creating the big document will replace the  \input{foo} by its content and LEAVE THE COMMENT, so that we are left with the line

    "using theorem \ref{LAB}, blah    % this is a comment"           (1)

    (in fact the comment itself is discarded but this is an other story : the point is that we get extra spaces and %)

    So when searching back the line, we are searching for the line (1) which does not exist in the actual code.


    HOW TO FIX MY CODE ?

    you should do one or more of the following
    - add an empty (or not empty) line after the line containing the fautive \\ref
    - remove the comment on the line containing the \input.

    """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


def ensure_unicode(s):
    """
    Return a 'unicode' object that represents 's'.
    No conversion if 's' is already unicode.

    str->unicode (via s.decode("utf8"))
    unicode->unicode (identity map)
    """
    if isinstance(s, str):
        return s.decode("utf8")
    if isinstance(s, unicode):
        return s
    testtype(s)
    raise TypeError("You are trying to convert to unicode the following object " +
                    str(s)+" of type "+str(type(s)))


def ensure_str(s):
    """
    Return a 'str' object that represents 's'.
    No conversion if 's' is already str.

    unicode->str (via s.encode("utf8"))
    str->str (identity map)
    """
    if isinstance(s, str):
        return s
    if isinstance(s, unicode):
        return s.encode("utf8")
    testtype(s)
    raise TypeError("You are trying to convert to unicode the following object " +
                    str(s)+" of type "+str(type(s)))


def logging(text, pspict=None):
    # text=ensure_unicode(text)
    if pspict:
        text = "in "+pspict.name+" : "+text
    print(text)
    with codecs.open(LOGGING_FILENAME, "a", encoding="utf8") as f:
        f.write(text+"\n")


def ensure_unicode(text):
    """
    No more useful since python3
    """
    return text


def testtype(s):
    print(s, type(s))


def RemoveComments(text):
    """
    Takes text as a tex source file and remove the comments including what stands after \end{document}
    Input : string
    Output : string
    """
    line_withoutPC = []
    # we remove the end of lines with % if not preceded by \
    pattern = "[^\\\]%"
    search = re.compile(pattern).search
    # This search only matches the % that are preceded by something else than \.
    # This does not match the % at the beginning of the line. This is why a second test is performed.
    for lineC in text.split("\n"):
        s = search(lineC)

        if s:
            ligne = s.string[:s.start()+2]    # We keep the "%" itself.
        else:
            ligne = lineC

        # % at the beginning of a line is not matched by the regex.
        if ligne.startswith("%"):
            ligne = "%"

        line_withoutPC.append(ligne)
    code_withoutPC = "\n".join(line_withoutPC)

    # Now we remove what is after \end{document}

    final_code = code_withoutPC
    if "\end{document}" in code_withoutPC:
        final_code = code_withoutPC.split("\end{document}")[0]+"\end{document}"
    return final_code


def random_string(length):
    """return a random string."""
    alphabet = string.ascii_lowercase+string.ascii_uppercase
    return "".join([random.choice(alphabet) for i in range(0, length)])


def human_timestamp(now=None):
    """Return a human readable timestamp."""
    if now is None:
        now = time.time()
    local_time = time.localtime(now)
    return time.strftime("%Z - %A  %Y/%B/%d, %H:%M:%S", local_time)


def json_serial(obj):
    """Serialize the datetime."""
    if isinstance(obj, datetime.datetime):
        timestamp = obj.timestamp()
        return human_timestamp(timestamp)
    return str(obj)


def read_json_file(json_path, default=None):
    """
    Return the given json file as dictionary.

    @param {string} `json_path`
    @return {dictionary}
    """
    json_path = Path(json_path)
    if not json_path.is_file():
        if default is None:
            raise ValueError(f"You try to read {json_path}. "
                             f"The file does not exist and you "
                             f"furnished no default.")
        return default
    with open(json_path, 'r') as json_data:
        try:
            answer = json.load(json_data)
        except json.decoder.JSONDecodeError as err:
            print("JSONDecodeError:", err)
            message = f"Json error in {json_path}:\n {err}"
            raise ValueError(message) from err
    return answer


def json_to_str(json_dict, pretty=False, default=None):
    """Return a string representation of the given json."""
    if pretty:
        return json.dumps(json_dict,
                          sort_keys=True,
                          indent=4,
                          default=json_serial)
    return json.dumps(json_dict, default=default)


def write_json_file(json_dict,
                    filename,
                    pretty=False,
                    default=None):
    """Write the dictionary in the given file."""
    my_str = json_to_str(json_dict, pretty=pretty, default=default)
    with open(filename, 'w') as json_file:
        json_file.write(my_str)


def text_hash(text):
    """Return a hash of a text."""
    m = hashlib.sha256()
    b_text = text.encode("utf8")
    m.update(b_text)
    return m.hexdigest()
