# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from common import *

def build(timestamp,scenario,architectures):
    for arch in architectures:
        fg_filename=cachedir(timestamp,scenario,arch)+'/fg-packages'
        rep_filename=cachedir(timestamp,scenario,arch)+'/summary'

        if not os.path.isfile(fg_filename):
            warning('no such file: '+fg_filename)
            return

        if not os.path.isfile(rep_filename):
            warning('no such file: '+fg_filename)
            return

        total_packages=lines_in_file(fg_filename)
        broken_packages=lines_in_file(rep_filename)

        if total_packages==0:
            percentage=0
        else:
            percentage=100*broken_packages/total_packages

        with open_weatherfile(scenario,arch,'w') as outfile:
            print(percentage,file=outfile)

    
