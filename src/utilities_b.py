
"""Some not so generic utilities related to pytex."""

import os
import sys
from pathlib import Path

from pytex.src.utilities import dprint

_ = dprint

class FileOutput(object):
    """
    A `FileOutput` object is intended to be given as `out` in
    `SummaryOutput`. Thus here the write` function always gets
    a single `str` argument, since the work of conversion from `*args` is
    done in `SummaryOutput.__call__`

    Creating an object does not empties the log file. The reasons is that
    one round of testing a document asks for several launch of `pytex`. Only
    the output of the last one would be available in the log file.

    However, here we check that the file exists; if not we create it.
    """

    def __init__(self, filename):
        self.filename = filename
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as f:
                f.write("Here is the log file")

    def write(self, text):
        sys.stdout.write(text)
        with open(self.filename, 'a') as f:
            f.write(text)



def ecrire(texte, couleur, output=None):
    # Noir 30 40, Rouge 31 41, Vert 32 42, Jaune 33 43, Bleu 34 44,
    # Magenta 35 45, Cyan 36 46, Blanc 37 47,
    # la police: 0->rien,  1->gras, 4->souligné, 5->clignotant, 7->inversée
    string = "\033[0;"+str(couleur)+";33m"+texte+"\033[0;47;33m"
    if output is None:
        print(string)
    else:
        output(string)



def ProducePytexCode(options):
    """
    See the docstring of Options
    return an object LatexCode because it has to be passed to plugins.
    """
    # The plugin has to do itself the work to apply inputs if he wants to.
    # The reason is that some plugin just want to deal with the main tex file.
    codeLaTeX = options.intermediate_code()
    return codeLaTeX


def CreateRoughCode(options):
    """
    Creates a latex file that is ready to be send to Arxiv.

    See docstring of LatexCode.rough_source.
    """
    rough_code = options.rough_code(options)
    rough_code.save(options.source_filename)
    print("I created the source", options.source_filename)
    return options.source_filename

def set_no_useexternal(A):
    r"""
    This plugin is automatically applied when 'pytex' is invoked with
    '--no-external'. You have to put something like this before
    '\begin{document}' :


    \newcounter{useexternal}
    \setcounter{useexternal}{1}
    \ifthenelse{\value{useexternal}=1}
            { \usetikzlibrary{external} \tikzexternalize }
            { \newcommand{\tikzsetnextfilename}[1]{} }

    This plugin will change the '1' into '0', in such a way that
    'external' will not be used.

    See position 2764113936
    """
    u = r"""\setcounter{useexternal}{1}"""
    A = A.replace(u, u.replace("1", "0"))
    return A


def randombase(n=6):
    """
    return a random string of (by default) 6 characters.
    """
    import random
    import string
    rb = ""
    for _ in range(0, n):
        rb = rb+random.choice(string.ascii_letters)
    return rb


class Sortie(object):
    def __init__(self):
        self.ps = False
        self.pdf = False
        self.nocompilation = False
        self.rough_source = False

class Compil(object):
    def __init__(self):
        self.simple = 1
        self.tout = 0
        self.lotex = True
        self.pdflatex = True
        self.dvi = False
        self.verif = 0


class SummaryOutput(object):
    """
    This class serves to replace `print` for the summary messages
    """

    def __init__(self, out):
        self.out = out

    def __call__(self, *args):
        text = ""
        for a in args:
            text = text+str(a)+" "
        self.out.write(text+"\n")


def arg_to_output(arg):
    """
    from a string of the form
    'output=<filename>'
    creates an output that prints on the screen and in the file.
    """
    filename = arg.split("=")[1]
    return SummaryOutput(FileOutput(filename))


def is_tex_file(elem:Path):
    """Say if the given filename is to be considered."""
    if not elem.is_file():
        return False
    if elem.suffix != ".tex":
        return False
    if "-source-" in str(elem):
        return False
    return True


def get_tex_files(directory:Path)->list[Path]:
    """Retutn the list of tex files in the given directory."""
    answer:list[Path] = []
    for elem in directory.iterdir():
        if is_tex_file(elem):
            answer.append(elem)
    return answer
