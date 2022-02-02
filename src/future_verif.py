# Copyright 2015-2017, 2019-2020
# Laurent Claessens
# contact : laurent@claessens-donadello.eu


"""Functions to test future references."""


import re
import os
import hashlib
import pygrep
from types import SimpleNamespace

from src.utilities import ReferenceNotFoundException
from src.future_reference import FutureReference

dprint = print


def is_tex_file(filename):
    """Say if the given filename is to be considered."""
    if not filename.endswith(".tex"):
        return False
    if "-source-" in filename:
        return False
    return True


def get_future_warning(rough_code, label_dict,
                       tested_label, reference, myRequest):
    """Return the warning corresponding."""
    label_pos = label_dict[tested_label].position
    if reference.position > label_pos:
        return None

    ok_hash = myRequest.ok_hash

    line_label = rough_code.position_to_line(label_pos)
    line_ref = rough_code.position_to_line(reference.position)

    line_label = line_label.replace("\n", "")
    line_ref = line_ref.replace("\n", "")

    h = hashlib.new("sha1")
    h.update(line_ref.encode("utf8"))
    hexdigest = h.hexdigest()

    if hexdigest in ok_hash:
        return None

    # 'star' is the list of files in which we are going to grep.
    star = []
    for directory in rough_code.input_paths:
        all_files = os.listdir(directory)
        star.extend([os.path.join(directory, x) for x in all_files
                     if is_tex_file(x)])

    label_lines = pygrep.grep(re.escape(line_label), star,
                              first_result=True)
    ref_lines = pygrep.grep(re.escape(line_ref), star,
                            first_result=True)

    if not ref_lines:
        print(f"A problem occurred searching for the line {line_ref}")
        message = "\n I'm not able to found back the " \
                  "future reference \\ref. Look at the " \
                  "docstring of ReferenceNotFoundException " \
                  "in Utilies.py for more details."
        raise ReferenceNotFoundException(message)

    if not label_lines:
        ref_line = ref_lines[0]
        message = f"Label {tested_label} not found for: {ref_line.matched}"
        print("")
        print("")
        print(message)
        print("")
        print("If this is a yanntricks reference, you have to add"
              " it in the `ok_hash` list because the `.pstricks`"
              " files are not included in the research for references."
              )
        print(hexdigest)
        default_label_line = SimpleNamespace(filename="filenotfound",
                                             linenumber=-1,
                                             string="not found.")
        label_lines = [default_label_line]

    label_line = label_lines[0]
    ref_line = ref_lines[0]

    return FutureReference(tested_label, label_line, ref_line,
                           myRequest, hexdigest=hexdigest)
