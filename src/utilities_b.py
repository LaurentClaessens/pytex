
"""Some not so generic utilities related to pytex."""


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

