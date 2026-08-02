"""Some other utilities to avoid cyclic imports."""

from pytex.src.all import FileToLogCode


def verif_grep(options):
    if options.nombre_prob > 1:
        options.output("Still "+str(options.nombre_prob) +
                       " problems to be fixed. Good luck !")
    if options.nombre_prob == 1:
        options.output(
            "Only one problem to be fixed. Next to perfection !!")
    x = FileToLogCode(options)
    options.output(x)


