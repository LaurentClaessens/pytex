# Copyright 2015-2017, 2019-2020
# Laurent Claessens
# contact : laurent@claessens-donadello.eu

"""Abstraction around a future reference."""


class FutureReference:
    """Represent a reference to the future."""
    def __init__(self, tested_label, label_line, ref_line,
                 myRequest, hexdigest):
        """Initialize."""
        self.tested_label = tested_label
        self.label_line = label_line
        self.ref_line = ref_line
        self.concerned_files = [self.label_line.filename,
                                self.ref_line.filename]
        self.hexdigest = hexdigest

        if self.hexdigest in myRequest.ok_hash:
            raise ValueError(f"__init__ : {self.hexdigest}")

    def output(self):
        """Print self."""
        print("")
        print("----------------------------")
        print("")
        print(f"{self.ref_line.filename} : {self.ref_line.linenumber}")
        colored_label = f"\033[0;33;33m{self.tested_label}\033[0;47;33m"
        str_line = self.ref_line.string
        print(str_line.replace(self.tested_label, colored_label))

        # Not test if ref_line.filename is already in concerned_files.
        # Thus the myRequest.append lines will appear
        # by pairs of linked files.

        print(f"{self.label_line.filename}: {self.label_line.linenumber}")

        str_line = self.label_line.string
        colored_label = f"\033[0;33;33m{self.tested_label}\033[0;47;33m"
        print(str_line.replace(self.tested_label, colored_label))

        print("hash: ", self.hexdigest)
