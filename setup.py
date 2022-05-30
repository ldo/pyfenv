#+
# Setuptools script to install pyfenv. Make sure setuptools
# <https://setuptools.pypa.io/en/latest/index.html> is installed.
# Invoke from the command line in this directory as follows:
#
#     python3 setup.py build
#     sudo python3 setup.py install
#
# Written by Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
#-

import setuptools

setuptools.setup \
  (
    name = "pyfenv",
    version = "0.5",
    description = "access to additional functionality in C99 fenv.h, for Python 3.4 or later",
    author = "Lawrence D'Oliveiro",
    author_email = "ldo@geek-central.gen.nz",
    url = "https://github.com/ldo/pyfenv",
    py_modules = ["fenv"],
  )
