#  PYTEX

## Presentation

A wrapper around `pdflatex` which gives some flexibility for compiling large files.

### What problem do we solve ?

Let say you have a (very) large LaTeX document that is divided into dozen or hundreds of `.tex` files (like [this one](http://laurent.claessens-donadello.eu/mazhe.html) for example -- 3500 pages). The usual mechanism that allows to compile only a part of the document is `\includeonly`.

The problems are :

* `\includeonly` implies that you input your `.tex` files with `\include`, which basically restricts you to only one file by chapter.
* Each time you want to compile an other part of the document, you have to change the `\includeonly` line.
 
### How do we solve ?

`pytex` is a python script that generates on the fly an intermediate `.tex` file and which launches `pdflatex` on it.

Suppose to have the LaTeX document `main.tex` as

```latex
\documentclass[a4paper,oneside,11pt]{book}

\input{preamble}

\chapter{First chapter}
\input{foo1}
\input{foo2}

\chapter{Second chapter}
\input{bar1}
\input{bar2}

\chapter{Third chapter}
\input{foo3}
\input{foo4}
```

If you want to compile the files `premable.tex`, `foo1` and `foo2` you creates the following file named `lst_example.py` :

```python
#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import unicode_literals

import LaTeXparser
import LaTeXparser.PytexTools

myRequest = LaTeXparser.PytexTools.Request()

myRequest.original_filename="main.tex"

myRequest.ok_filenames_list=["preamble"]
myRequest.ok_filenames_list.extend(["foo1"])
myRequest.ok_filenames_list.extend(["foo3"])

myRequest.new_output_filename="MySmallPart.pdf"
```

and you compile with
 
    pytex lst_example.py

This will generates `MySmallPart.pdf` containing the result of the compilation with only `premable`, `foo1` and `foo2` (and also some intermediate files).

## Installation and dependencies

* Download [LaTeXparser](https://github.com/LaurentClaessens/LaTeXparser) and save it somewhere Python will be able to find.

* Download [pytex](https://github.com/LaurentClaessens/pytex) and save it somewhere bash will be able to find.


## Other functionalities

* `pytex` generates on the fly an intermediate `.tex` file that contains the requested `\input` lines. You can perform arbitrary string manipulations in Python on that file before the compilation. Some are predefined.

* `pytex` will compile as much times as necessary for all the cross-references to be done.

* `pytex` reads the `.aux` file and presents the missing and multiple labels in a convenient way.

* The option `--verif` checks if the document contains `\ref` or `\eqref` for which the corresponding `\lable` lies later in the document (in a text math, one should refer to theorems that will be proven later). You can define exceptions : sentences that you allow to refer to "future" label.

* `pytex` inherits from the functionalities of [LaTeXparser](https://github.com/LaurentClaessens/LaTeXparser).

## Examples

* The documents [le frido](http://laurent.claessens-donadello.eu/pdf/lefrido.pdf) and [mazhe](http://laurent.claessens-donadello.eu/pdf/mazhe.pdf) are created from the same main [LaTeX file](https://github.com/LaurentClaessens/mazhe). `pytex` performs quite a lot of "pre-compilation" work on the fly. Notice by example the fact that the first is not divided in parts while the second is.

* The paper [BTZ black hole from the structure of so(2,b)](http://arxiv.org/pdf/0912.2267v3.pdf) is divided in two parts : one "short version" and one "long version" that share a lot of text. Believe it or not : there is *no code duplucation* on my computer. I wrote only once each statements and `pytex` made the work or recomposing the `tex` file. There are of course a lot of code duplication in the `tex` file I uploaded, which was automatically generated.

## TODO


## TEST

