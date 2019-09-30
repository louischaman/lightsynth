# Light demo processing project

This demo is written in pyprocessing, which uses jython and hence is python 2.7 compatible. It is difficult to load any external python packages into jython except by the 'standard' pyprocessing way, which is to compile any code it finds in the project directory. Therefore to run the project we must copy any dependencies into the project. 

This leaves some manual work to do to make sure the code in the processing project is up-to-date with changes that occur in the main directory, and with the yaml library we use. The `_yaml` folder contains a copy of the pure python 2 implementation of pyyaml 5.1.1 copied from its source tarball. It is prefixed with an underscore to prevent shadowing the system-level yaml module from pyyaml installed via pip.

There's also an annoyance with loading files in processing: it doesn't seem to work. You're supposed to put data files in a `data` subdirectory and use the builtin `loadStrings` function, but this fails silently for me. You can still load files with the standard python function `open`, but you must supply an absolute path because behind the scenes processing copies the project to a temporary location before running files, and annoyingly it doesn't seem to copy the data files over.

In the demo clicking the mouse sends a dmx message of value 200 to each channel in squence. Press r to reload the lights and start again from channel 1.

In this folder `devices` contains some class definitions for dmx devices, and `gen_lights.py` is a python script for generating some example light setup yaml files.
