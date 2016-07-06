#  FRTEX

## Installation and dependencies

* download the actor system from [github](https://github.com/LaurentClaessens/actors)
* compile the actor system :
<pre> <code> $  mvn package   </code>  </pre>
* make it available :
<pre><code>$ mvn  install:install-file -Dfile=path-to-actors/target/actors.jar</code></pre>
* download `frtex` from [github](https://github.com/LaurentClaessens/frtex)
* Use `frtex` by example performing the tests :
<pre><code>$ mvn  test</code></pre>


## The Latex actor system

The "latex actor system" is intended to take as input a LaTeX filename and produce as output the "recursive" content of that file with all the \input{file} explicitly replaced by the content of "file.tex". 

The use of our actor system makes the recomposition work extremely multi-thread and then(?) efficient.

This is still under development.

### How it works

The behaviour of an actor is :

- read its LaTeX file
- create a list of the inputed files.
- for each of them, ask an other actor to make the job.
- when all the answers are received, recompose the LaTeX file
- send the result to the actor whose asked.

### What you need to know

The only class you have to work with is `LatexCode`. That class provides an abstraction that hides the actor system to the user.

### Working actor vs. Active actor

A `LatexActor` can be active or not, as any actor. The `LatexActor` has an other status that is "working" or not.

An actor which is requested to create the code of the file "foo.tex" reads this file and send a request message to a new actor each time that it encounters a "\input" in "foo.tex". Such an actor has to be able to read new messages since it relies on the answer messages in order to complete its work.

So such a working actor is set "inactive" in order to unlock its mail box. But it is still working and cannot be requested to work on an other tex file until "foo.tex" is completed and sent to the calling actor.

The `LatexActorSystem` has a method 

```java
public LatexActorRef getNonWorkingActor()
```
which return an actor reference to an actor who can be requested to deal with a new tex file. The actor is 'working' from the moment it is returned.

### Latex message

The latex actor system recognize two types of messages.

* `LatexMessage` (abstract)
* `LatexRequestMessage` (extends `LatexMessage`)
* `LatexAnswerMessage` (extends `LatexMessage`)

### Hypothesis on the LaTeX source code (simplification and limitations)

* The filenames are more or less standard. Like only one dot, no curly braces and so on.

* The percent symbol should always mean a comment, with the exception of "\%". This can be a limitation if you have URL in which you substituted special characters with their %xx representation.

* If a file in inputed more than once, it will be computed at each input. Moreover, this is a static tool, so you cannot do
```latex
\input{foo}
% something that modify foo.tex during the LaTeX compilation.
\input{foo}
```

* More generally, if your LaTeX compilation itself create/modify a file that is then inputed, you cannot hope `frtex` to make its job.

* The LaTeX code is supposed to be encoded in utf8

* The `\input` has to be explicit. `frtex` will not make the substitution on
```latex
\newcommand{\myInput}[1]{\input{#1}}
\myInput{foo}
```

* In the same spirit, `\lstinput` from package `listingutf8` will not be recognized. It is however in my plans to make it in the future (send me a patch).

* When inputing a tex file, use
```latex
\input{foo}
```
and not
```latex
\input{foo.tex}
```
 * Filename must contain (at most) one dot. You cannot do
```latex
\input{fdl-1.3}
```
for implying an input of `fdl-1.3.tex`. And even less
```latex
\input{fdl-1.3.tex}
```

### Not standalone

The produced LaTeX code is in general not a standalone that can be fed to `pdflatex`. 

* Commands like `\inlcudegraphic` or `\lstinputlisting` are including external files that are not processed here. 

* For the bibliography, it is in project to make the replacement of `\bibliography{foo}` by the content of `foo.bbl`.

* In particular for [mazhe](https://github.com/LaurentClaessens/mazhe), the exercices are included by the macro `\Exo` that makes a conditional `\input`.

These points explain why the test directory `mazhe_tex_test` is so large : this is a real live test, and the real live does not fulfills the limitations of some softwares (one should fix the live).

### Bugs

The input mechanism in LaTeX seems complex and I didn't study it. In particular, what makes the space after an input ? [This question](http://tex.stackexchange.com/questions/317361/how-does-input-adds-a-space) has an answer that is too complicated for me.

If someone can explain me that clearly, I'd appreciate.

```latex
\documentclass{minimal}     
\begin{document}            
                            
AB                          
                            
\input{1_file}\input{2_file}
                            
\input{1_file}              
\input{2_file}              
                            
\end{document}              
```

with `1_file.tex` containing only "A" and `2_file.tex` containing "B" (no 'new line' or something). `frtex` will add a `\n` after the input *if* it is not followed by an other `\n`. So it will translate the second and third examples in the same way. LaTeX makes a difference that I do not understand.

```latex
\begin{equation}
\input{foo}
\end{equation}
```
with `foo.tex` containing "a=b" does not provoke error. This is why `frtex` does not add a "\n" if the input statement is already followed by a newline.

Fixing this bug would require pure LaTeX (not Java) knowledge that I don't have. In particular, clearly understand the answer [here](http://tex.stackexchange.com/questions/317361/how-does-input-adds-a-space).

### TODO

I sometimes have a `NullPointerException` in `MultiFIFOMap.poll`. Not always. Search in progress ...

### TEST

use `mvn test` to see the result.

Notice that this software is still under development. I try to not commit (and even less push) versions that do nothing else than a crash...
