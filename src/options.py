"""
The options object.

Follow the anti-pattern of the god object ... hum ...
"""

import os
import sys
import subprocess
from pathlib import Path

from src.utilities_b import Sortie
from src.utilities_b import SummaryOutput
from src.utilities_b import Compil

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

    def __init__(self, arguments):
        self.arguments = arguments

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
        for arg in self.arguments:
            if arg[0] != "-":
                self.LireFichier(arg)
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
        self.pytex_filename = self.pwd+"/"+"Inter_"+self.prefix+"-" + \
            os.path.basename(self.original_file).replace(".tex", "_pytex.tex")
        self.source_filename = self.pwd+"/"+self.prefix + \
            "-source-"+os.path.basename(self.original_file)

        if self.Compil.tout == 1:
            self.source_filename = self.pwd+"/all-" + \
                os.path.basename(self.original_file)
            self.pytex_filename = self.pwd+"/all-" + \
                os.path.basename(self.original_file).replace(
                    ".tex", "_pytex.tex")
        self.log_filename = self.pytex_filename.replace(
            "_pytex.tex", "_pytex.log")

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

    def future_reference_verification(self, options, fast=True):
        r"""
        Print the list of references that are made to the future.

        If fast is true, make more assumptions on the LaTeX code.
        You will only catch references and label like
        \ref{foo}
        \label{bar}
        while not matching
        \ref
        {foo}
        or
        \label{foo\Macro{bar}boor}
        """

        # rough_code with fast=True is buggy.
        rough_code = self.rough_code(options, fast=False)

        print("Analysing the document for label")
        labels = rough_code.search_use_of_macro("\label", 1, fast=fast)

        print("Analysing the document for ref")
        ref = rough_code.search_use_of_macro(r"\ref", 1, fast=fast)

        print("Analysing the document for eqref")
        eqref = rough_code.search_use_of_macro("\eqref", 1, fast=fast)

        ref_dict = {}
        label_dict = {}

        print("Working on future references ...")

        for occ in labels:
            label = occ.arguments[0]
            ref_dict[label] = []

        references = ref[:]
        references.extend(eqref)

        for occ in references:
            label = occ.arguments[0]
            ref_dict[label] = []

        for occ in references:
            label = occ.arguments[0]
            ref_dict[label].append(occ)

        for occ in labels:
            label = occ.arguments[0]
            if label in label_dict.keys():
                output("The label <{0}> is used multiple times".format(label))
                output("Here is the last time I see that")
                output(occ.as_written)
                raise NameError
            label_dict[label] = occ

        # The future references are detected in 'rough_code'
        # which is a large latex code recursively generated by applying
        # all the \input.
        # Let us say we found the line
        # "From the Stone theorem \ref{tho_stone} we deduce that blabla"
        # This line belongs to 'rough_source'
        # In order to provide the user with an useful information we have
        # to find back the line in the original sources.
        # That is grepping the line in the real sources.

        # For each future references, there are two concerned files
        # (maybe the same) :
        # the one in which we found the \(eq)ref and the one in which
        # is the corresponding \label. The 'concerned_files' list keeps is list
        # of the files that are concerned by a future references.
        future_warnings = []
        for tested_label in label_dict.keys():
            for ref in ref_dict[tested_label]:
                warning = get_future_warning(rough_code, label_dict,
                                             tested_label, ref,
                                             self.myRequest)
                if warning:
                    future_warnings.append(warning)

        concerned_files = set()
        total_futur = 0
        hexdigests = []
        for warning in future_warnings:
            # The function `has_to_be_printed` is defined in
            # the file `lst_foo.py`.
            if self.myRequest.has_to_be_printed(warning):
                warning.output()
                hexdigests.append(warning.hexdigest)
                total_futur += 1
                for futur_file in warning.concerned_files:
                    concerned_files.add(futur_file)

        print("All the wrong hashes:")
        for hexdigest in hexdigests:
            dprint(hexdigest)
        print(f"Number of future references: {total_futur}")
        print("concernd files:")
        for futur_file in concerned_files:
            print(futur_file)

    def make_final_copy(self, pdf_output, new_filename):
        """
        Copy 'pdf_output' to 'new_filename'

        - 'pdf_output' is supposed to be the filename produced by pdflatex itself.
        - 'new_filename' is the name we want to use.

        The main point of this function is not the copy itself (shutil.copy2), but the fact
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
                "This is a problem about synctex. {0} do not exist".format(output_synctex))
            # TODO : this message produces an unicode error when there are accents in the path name.
        shutil.copy2(output_synctex, new_output_synctex)

    def copy_final_file(self):
        """
        It is intended to be used after the compilation. It copies the 'pdf' resulting file to a new one.
        The aim is to let the pdf viewer with the same pdf file until the last moment.

        The difference between `new_output_filename` and `new_output_filenames` is that the latter is a list.
        When `new_output_filenames` is given, we produce as much files as given new filenames.
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

        We take as basis the pytex filename because the bibliography is created (via bibtex) when we
        compile that one.
        """
        return self.pytex_filename.replace("_pytex.tex", "_pytex.bbl")

    def index(self):
        """ retourne le fichier ind qui correspond au fichier principal """
        return self.pytex_filename.replace("_pytex.tex", "_pytex.ind")

    def NomVersChemin(self, nom):
        return self.pwd+"/"+nom

    def LireFichier(self, nom):
        """
        If the file extension is .py, interpret it as a module and we extract the relevant informations.
        module.plugin_list  : a list of functions that will be applied to the LaTeX code before to give it to LaTeX
        module.original_file
        module.ok_filenames_list
        """
        FichierReq = self.NomVersChemin(nom)
        self.prefix = os.path.basename(FichierReq).replace(
            ".py", "").replace("lst-", "").replace("lst_", "")
        if FichierReq.endswith(".py"):

            sys.path.append(os.path.dirname(FichierReq))
            module_filename = os.path.basename(FichierReq.replace('.py', ''))
            module = importlib.import_module(module_filename)

            self.myRequest = module.myRequest

            # See explanatons at position 2764113936
            if "--no-external" in sys.argv:
                self.myRequest.add_plugin(set_no_useexternal, "after_pytex")

            # This is the application of a plugin on Options itself,
            # see note  25637
            # position ooMEVCoo
            for plugin in [x for x in self.myRequest.plugin_list if x.hook_name == "options"]:
                plugin(self)

            #self.original_file = manip.Fichier(self.myRequest.original_filename)
            self.original_file = self.myRequest.original_filename
            self.new_output_filename = self.myRequest.new_output_filename
            self.new_output_filenames = self.myRequest.new_output_filenames
            self.ok_filenames_list.extend(
                [x.replace(".tex", "") for x in self.myRequest.ok_filenames_list])
        if FichierReq.endswith(".lst"):
            self.listeFichPrendre.append(FichierReq)

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
        for plugin in self.myRequest.plugin_list:
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
