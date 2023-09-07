"""
The options object.

Follow the anti-pattern of the god object ... hum ...

Note 25637 : THE PLUGIN TYPES

* 'options' :
    applied to the Options itself, it is applied after the import
* 'before_pytex' :
    applied on the text (as sting) before to create the pytex file.
* 'after_pytex' :
    applied on the LaTeXCode of the pytex file.
* 'before_compilation' :
    applied on nothing, before the compilation.
    Such a plugin does not return anything. It is devoted to perform
    some checks before to compile.
    Example : check that a file exist before to compile,
    or write a greeting to the user.

* 'after_compilation' :
    applied on nothing, after the compilation.
    Such a plugin does not return anything. It is devoted to
    perform some checks after compilation.
    Example : check that a file has been created or make
    some research in the auxiliary files.

Options :
    --no-compilation
        Do not compile, but produce the final _pytex.tex file and
        print the commands that were to be launched without.
    --rough-source
        Output an extremely hard-coded pytex file which is
        ready for ArXiv.

    --output=<filame>
        Output the summary informations in <filename>.
        This does not empties the file if it exists,
        but creates it if it does not exist.

"""


import os
import sys
import subprocess
from pathlib import Path

from pytex.src.utilities_b import Sortie
from pytex.src.utilities_b import Compil
from pytex.src.utilities_b import arg_to_output
from pytex.src.utilities_b import SummaryOutput
from pytex.src.utilities_b import set_no_useexternal
from pytex.src.utilities_b import CreateRoughCode
from pytex.src.utilities_b import ProduceIntermediateCode
from pytex.src.utilities_b import ProducePytexCode
from pytex.src.utilities_b import randombase
from pytex.src.grep_wrapper import PytexGrep
from pytex.src.all import FileToLatexCode
from pytex.src.utilities import logging
from pytex.src.all import FileToText
from pytex.src.PytexTools import Compilation


dprint = print


class Options(object):
    r"""
    self.original_file : the original file, written by hand
    self.intermediate_code() : LatexCode object containing the same
                    as original_file but with
                    removed \input that are not in the list.
                    This does not has to be written in a real file.
    self.pytex_file : all the remaining \input are explicitly performed.
                (the bibliography/index still have to be created
                by bibtex/makeindex)
                This file still contains the comments.
                This is the one to be usually compiled.
    self.source_file : the file with everything explicit including the
                bibliography and the index.  The comments are removed.
                This is for Arxiv.
    """

    def __init__(self, my_request):

        self.my_request = my_request
        self.pwd = subprocess.getoutput("pwd")  # .decode("utf8")
        self._pytex_file = None
        self._intermediate_code = None
        # Cette liste sont les fichiers .tex à accepter par input
        self.ok_filenames_list = []
        # Cette liste sont les fichiers .tex qui sont à refuser par input
        self.refute_filenames_list = []
        self.Sortie = Sortie()
        self.Compil = Compil()
        self.Compil.verif = False
        self.plugin_list = []
        self.before_pytex_plugin_list = []
        self.nombre_prob = 0
        self.new_output_filename = None  # see copy_final_file
        self.new_output_filenames = None
        self.output = SummaryOutput(sys.stdout)
        self.read_request()
        for arg in sys.argv:
            if arg == "--all":
                self.Compil.tout = 1
            if arg == "--verif":
                self.Compil.verif = True
                self.Compil.lotex = False
            if arg == "--no-compilation":
                self.Sortie.nocompilation = True
            if arg == "--rough-source":
                self.Sortie.rough_source = True
                self.Sortie.nocompilation = True
            if "--output=" in arg:
                self.output = arg_to_output(arg)

        self.listeFichPris = []

        self.pytex_filename = Path(self.pwd) / \
            f"Inter_{self.prefix}-{self.original_file.stem}_pytex.tex"

        # self.pytex_filename = self.pwd+"/"+"Inter_"+self.prefix+"-" + \
        #    os.path.basename(self.original_file).replace(".tex", "_pytex.tex")

        self.source_filename = Path(
            self.pwd) / f"{self.prefix}-source-{self.original_file.name}"

        # self.source_filename = self.pwd+"/"+self.prefix + \
        #    "-source-"+os.path.basename(self.original_file)

        if self.Compil.tout == 1:
            self.source_filename = self.pwd+"/all-" + \
                os.path.basename(self.original_file)
            self.pytex_filename = self.pwd+"/all-" + \
                os.path.basename(self.original_file).replace(
                    ".tex", "_pytex.tex")

        self.log_filename = self.pytex_filename.parent / \
            f"{self.pytex_filename.stem}.log"
        # self.log_filename = self.pytex_filename.replace(
        #    "_pytex.tex", "_pytex.log")

        self.pytex_grep = PytexGrep(Path.cwd())

    def grep(self, command, label):
        return self.pytex_grep.grep(command, label)

    def accept_input(self, filename):
        if filename not in self.ok_filenames_list:
            return False
        if filename in self.refute_filenames_list:
            return False
        return True

    def rough_code(self, options, fast=False):
        codeLaTeX = FileToLatexCode(options.pytex_file())
        print("Creating rough code")
        rough_code = codeLaTeX.rough_source(
            options.source_filename,
            options.bibliographie(),
            options.index(), fast=fast)
        return rough_code

    def make_final_copy(self, pdf_output, new_filename):
        """
        Copy 'pdf_output' to 'new_filename'

        - 'pdf_output' is supposed to be the filename
                       produced by pdflatex itself.
        - 'new_filename' is the name we want to use.

        The main point of this function is not the
        copy itself (shutil.copy2), but the fact
        to manage the ".synctex.gz" files in the same time.
        """
        import shutil
        logging("Copy : "+pdf_output+" --> "+new_filename)
        shutil.copy2(pdf_output, new_filename)

        # One has to copy the file foo.synctex.gz to  0-foo.synctex.gz
        output_synctex = pdf_output.replace(".pdf", ".")+"synctex.gz"
        new_output_synctex = new_filename.replace(".pdf", ".synctex.gz")
        if not os.path.exists(output_synctex):
            raise NameError(
                "This is a problem about synctex. "
                f"{output_synctex} do not exist")
        shutil.copy2(output_synctex, new_output_synctex)

    def copy_final_file(self):
        """
        It is intended to be used after the compilation.

        It copies the 'pdf' resulting file to a new one.
        The aim is to let the pdf viewer with the same pdf
        file until the last moment.

        The difference between `new_output_filename` and
        `new_output_filenames` is that the latter is a list.
        When `new_output_filenames` is given, we produce as
        much files as given new filenames.
        """
        tex_filename = os.path.split(self.pytex_filename)[1]
        pdf_output = tex_filename.replace(".tex", ".pdf")

        # new_filenames contains both
        # 'new_output_filename' and 'new_output_filenames'
        new_filenames = []
        if self.new_output_filename is not None:
            new_filenames.append(self.new_output_filename)
        if self.new_output_filenames is not None:
            new_filenames.extend(self.new_output_filenames)

        # fix the default is nothing is given
        if new_filenames == []:
            new_filenames = ["0-"+pdf_output]

        for f in new_filenames:
            self.make_final_copy(pdf_output, f)

    def bibliographie(self):
        """
        Return the bbl file that corresponds to the principal file

        We take as basis the pytex filename because the
        bibliography is created (via bibtex) when we compile that one.
        """
        return self.pytex_filename.replace("_pytex.tex", "_pytex.bbl")

    def index(self):
        """ retourne le fichier ind qui correspond au fichier principal """
        return self.pytex_filename.replace("_pytex.tex", "_pytex.ind")

    def NomVersChemin(self, nom):
        return self.pwd+"/"+nom

    def read_request(self):
        """
        If the file extension is .py, interpret it as a module
        and we extract the relevant informations.

        module.plugin_list  : a list of functions that will
        be applied to the LaTeX code before to give it to LaTeX
        module.original_file
        module.ok_filenames_list
        """
        self.prefix = self.my_request.prefix

        # See explanatons at position 2764113936
        if "--no-external" in sys.argv:
            self.my_request.add_plugin(set_no_useexternal, "after_pytex")

        # This is the application of a plugin on Options itself,
        # see note  25637
        # position ooMEVCoo
        for plugin in [x for x in self.my_request.plugin_list
                       if x.hook_name == "options"]:
            plugin(self)

        self.original_file = self.my_request.original_filename
        self.new_output_filename = self.my_request.new_output_filename
        self.new_output_filenames = self.my_request.new_output_filenames
        self.ok_filenames_list.extend(
            [x.replace(".tex", "") for x in self.my_request.ok_filenames_list])

    def create_rough_source(self, filename):
        """
        Write the file that contains the source code to
        be sent to Arxiv in the file <filename>.
        """
        self.source_filename = filename
        CreateRoughCode(self)

    def intermediate_code(self):
        if not self._intermediate_code:
            self._intermediate_code = ProduceIntermediateCode(self)
        return self._intermediate_code

    def apply_plugin(self, A, hook_name):
        """
        The plugin on the options object itself are called
        at the position ooMEVCoo
        """
        for plugin in self.my_request.plugin_list:
            if plugin.hook_name != hook_name:
                continue
            print("Applying the plugin", plugin.fun, plugin.hook_name)
            if hook_name in ["before_compilation",
                             "after_compilation"]:
                plugin.fun(self)
            else:
                A = plugin(A)
        return A

    def pytex_file(self):
        if self._pytex_file:
            return self._pytex_file

        A = FileToText(self.original_file)

        A = self.apply_plugin(A, "before_pytex")
        self.text_before_pytex = A

        # The conversion text -> LatexCode is done here
        A = ProducePytexCode(self)

        A = self.apply_plugin(A, "after_pytex")

        # Writing \UseCorrectionFile does not work because
        # of \U which is a Unicode stuff causing a syntax error.
        # But Writing \\UseCorrectionFile will not
        # work neither because it will write an explicit
        # \\UseCorrectionFile in the LaTeX file.

        rbase = randombase()
        A = A.replace(r"""\begin{document}""", r"""\begin{document}
                    \makeatletter
\@ifundefined{UseCorrectionFile}{}{"""+"\\"+r"""UseCorrectionFile{AEWooFLTbT}}
\makeatother
                    """.replace("AEWooFLTbT", "CorrPytexFile"+rbase+"corr"))

        A.save(self.pytex_filename)
        self._pytex_file = A.filename

        return self.pytex_file()

    def compilation(self):
        self.apply_plugin("", "before_compilation")
        pytex_filename = self.pytex_file()
        return Compilation(
            pytex_filename,
            self.Sortie.nocompilation,
            pdflatex=self.Compil.pdflatex,
            dvi=self.Compil.dvi
        )
