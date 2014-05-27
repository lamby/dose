# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, datetime
from common import *

xml_template='''<weather>
  <bundle>
    <id>{scenario}</id>
    <description>{description}</description>
  </bundle>
  <architecture>{architecture}</architecture>
  <date>{date}</date>
  <packages>
    <total>{number_total}</total>
    <broken>{number_broken}</broken>
  </packages>
  <index>{weather}</index>
  <url>{summary_url}</url>
</weather>'''

def weather_index(percentage):
    '''
    return a weather index for a percentage of broken packages
    1: sunny
    2: light clouds
    3: overcast
    4: showers
    5: storm
    '''

    if percentage <= 1:
        return(1)
    elif percentage <= 2:
        return(2)
    elif percentage <= 3:
        return(3)
    elif percentage <= 4:
        return(4)
    else:
        return(5)

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
            print(xml_template.format(
                    scenario=scenario,
                    description=scenario,
                    architecture=arch,
                    date=datetime.date.fromtimestamp(float(timestamp)),
                    number_total=total_packages,
                    number_broken=broken_packages,
                    weather=weather_index(percentage),
                    summary_url=url_summary(timestamp,scenario,arch)),
                  file=outfile)

    
