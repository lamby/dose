# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from common import *

def weather_report(timestamp,scenario,architecture):
    fg_filename=cachedir(timestamp,scenario,architecture)+'/fg-packages'
    rep_filename=cachedir(timestamp,scenario,architecture)+'/summary'

    if not os.path.isfile(fg_filename):
        warning('no such file: '+fg_filename)
        return

    if not os.path.isfile(rep_filename):
        warning('no such file: '+fg_filename)
        return

    total_packages=lines_in_file(fg_filename)
    broken_packages=lines_in_file(rep_filename)

    percentage=100*broken_packages/total_packages

    with open_weatherfile(scenario,architecture,'w') as outfile:
        print(percentage,file=outfile)

    
