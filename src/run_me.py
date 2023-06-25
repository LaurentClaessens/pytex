
import sys

from pytex.src.options import Options
from pytex.src.all import FileToLogCode
from pytex.src.utilities_b import verif_grep
from pytex.src.future_verification import future_reference_verification
_ = [sys]


dprint = print


def do_latex_more(options):
    """Say if one has to compile more."""

    if options.Compil.verif:
        return False
    if options.Compil.lotex:
        return False
    if options.Compil.simple != 1:
        return False
    if options.Sortie.pdf != 0:
        return False
    return True


def RunMe(my_request):
    options = Options(my_request)
    try:
        options.myRequest.run_prerequistes(options)
    except AttributeError:
        pass
    if options.Sortie.rough_source:
        options.create_rough_source(options.source_filename)

    if do_latex_more(options):
        options.compilation().latex_more(options)
        options.copy_final_file()

    if options.Compil.lotex:
        on = True
        while on:
            options.compilation().latex_more(options)
            options.copy_final_file()
            x = FileToLogCode(options, stop_on_first=True)
            on = x.rerun_to_get_cross_references(stop_on_first=True)
    if not options.Sortie.nocompilation and not options.Compil.verif:
        verif_grep(options)
    if options.Sortie.nocompilation:
        print("Le fichier qui ne fut pas compilé est", options.pytex_filename)
    else:
        print("Le fichier qui fut compilé est", options.pytex_filename)
        options.apply_plugin("", "after_compilation")
    if options.Compil.verif:
        future_reference_verification(options)
