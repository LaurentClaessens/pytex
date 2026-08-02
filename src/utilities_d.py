"""Some other utilities to avoid cyclic imports."""



def ProduceIntermediateCode(options):
    from pytex.src.all import string_to_latex_code
    codeLaTeX = string_to_latex_code(options.text_before_pytex)
    if options.Compil.tout == 0:
        list_input = codeLaTeX.search_use_of_macro(r"\input", 1)
        begin_document = codeLaTeX.find("\\begin{document}")
        for occurrence in list_input:
            A = occurrence.analyse()
            # If an "\input" is before "\begin{document}", we keep it.
            # This behaviour is due to the fact that some
            # "\input" are in the preamble,
            # inside \newcommand for example.
            if A.position > begin_document:
                if not options.accept_input(A.filename):
                    codeLaTeX = codeLaTeX.replace(occurrence.as_written, "%")
                else:
                    pass
    return codeLaTeX
