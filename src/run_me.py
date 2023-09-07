import sys

from pytex.src.options import Options
from pytex.src.all import FileToLogCode
from pytex.src.utilities_b import verif_grep
from pytex.src.future_verification import future_reference_verification
_ = sys


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
