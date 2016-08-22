# Reflexif
Reflexif is a pure Python Exif library that will be developed here
from existing code of my own that is lying around in my private repositories.
**It is not ready to be used yet. This README will be updated as
the development progresses.**

The planned core features cover:
 - a low-level API to read and write (raw) Exif/TIFF data structures
 - a high-level API to read and write Exif tags as key-value pairs
   that allows a high degree of control over the writing process
 - a transparent (and controllable) mapping between raw values and
   normalized / pretty print values
 - a plugin architecture to implement makernotes, custom value mappings
   and other hairy bits separately from the rest of the project

Reflexif will take special emphasis on providing a sensible low level API
that exposes the actual TIFF/IFD data structures, which is important
if you want to control the process of how modified Exif tags are written
to a file (which again is cumbersome and possibly hazardous).

The most important use case I have myself is a minimally invasive
modification of Exif tags in my orignal digital images
(e.g. orientation, timestamps, geotags), without keeping duplicates
and without having the entire Exif data and/or Image file rewritten.

# Documentation
[This repository](https://github.com/chschmitt/reflexif) acts
as the official project homepage. A separate sphinx documentation
will be hosted somewhere else at some point in the future. For the
time being, please consult the source code.

# Installation and usage
When the time has come, I will provide
a setup.py file and upload the project on PyPI. This will enable the
installation via pip (from PyPI of from this repository).

In the meantime, if you fancy a try, clone into this repository and
add the `main` folder to your `PYTHONAPTH`.

# Why another Exif library?

**TL;DR** *I think that a permissive-licensed Exif library that
provides low-level access to the Exif data structeres and that
is entirely written in Python might address an acutal gap in
the Python ecosystem.*

As with every new software project, you may of course challenge
whether there is an actual need for it. While thers is IMHO no
definitive answer to that, there are a few reaons for me
to develop Reflexif.

## Low level access to Exif/TIFF data structures
The usual functionality that is provided by Exif libraries to
the using application is to read (and sometimes write)
Exif tags as key-value pairs.
This is a useful abstraction for high-level APIs to access
Exif data. Logically, the complexity of the data structures
and especially the manipulation/writing process is then usually
hidden.
If it is important to you, how your image files are modified,
this may leave you with too little transparency or even control.

## Pure Python implementation
The arguably most complete Exif implementation that can be
used with Python is [exiv2](http://exiv2.org). It is available
via [gexiv2](https://wiki.gnome.org/Projects/gexiv2) (a GObject wrapper)
and [pygobject](https://wiki.gnome.org/Projects/PyGObject)
(a generic GObject binding for Python).

While exiv2 is a great piece of software, I do not like
the detours you have to take to use it with Python. If you want to
know what I mean, please try compiling gexiv2 and its dependencies on
a machine that has an outdated version of glib.

## Permissive license
I am a big fan of open source and the goals of the GPL. However,
I do not know where the projects I am dealing with will take
me eventually. So I chose not to rely too heavy on GPL'ed
libraries (such as gexiv2). 

In addition, permissive licenses are the normal case in the Python ecosystem
in terms of numbers (see PyPI) and (IMHO) user expectations, since most
of the large and prominent Python projects (such as NumPy or Django)
use permissive licenses.

# Compatibility and dependencies
For now, Reflexif will be developed and tested against CPython 3.5.
Compatibility with CPython 3.3+ will be tested and ensured later.
Depending on feedback and need, 

# Roadmap and Versioning
There is no roadmap with dates and milestones as I am working on Reflexif
on my own accord and when I have the time to do so.

Reflexif will use semantic versioning. Prior to release 1.0.0, breaking changes
may occur at any increment. Everything will take place in the master branch.

# Contributing
I am open to receive pull requests. If you plan larger contributions or
changes to Reflexif, please ope and issue first in order to make sure
that everything fits in nicely. By submitting a pull request, you accept
to publish your contributions under the same license. You will be added
to the `AUTHORS` file.

**Note**: Since I am currently the only author and copyright holder, there is only me
in the [`LICENSE`](LICENSE) and there is no `AUTHORS` file to keep things simple for now.
This will be changed when the first contribution will be merged into the repo.

# License
This project published under the 3-clause BSD license. See [`LICENSE`](LICENSE)



