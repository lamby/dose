# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, datetime
import conf
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

def icon(index):
    '''
    associate an icon to a weather index (as returned by weather_index)
    '''
    icon={1: 'weather-clear_sml.png',
          2: 'weather-few-clouds_sml.png',
          3: 'weather-overcast_sml.png',
          4: 'weather-showers-scattered_sml.png',
          5: 'weather-storm_sml.png'
          }
    text={1: 'sunny',
          2: 'clouds',
          3: 'overcast',
          4: 'rain',
          5: 'storm'
          }
    return('<img src="../../weathericons/{i}" alt="{t}">'.format(
            i=icon[index],t=text[index]))

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

        # with open_weatherfile(scenario,arch,'w') as outfile:
        #     print(xml_template.format(
        #             scenario=scenario,
        #             description=conf.scenarios[scenario]['description'],
        #             architecture=arch,
        #             date=datetime.date.fromtimestamp(float(timestamp)),
        #             number_total=total_packages,
        #             number_broken=broken_packages,
        #             weather=weather_index(percentage),
        #             summary_url=url_summary(timestamp,scenario,arch)),
        #           file=outfile)
        with open(cachedir(timestamp,scenario,arch)+'/weather', 'w') as outfile:
            print(weather_index(percentage),file=outfile)

def write_available():
    info('Describing available weather reports')
    with open_weather_available_file('w') as outfile:
        print('<weathers>',file=outfile)
        for scenario in conf.scenarios.keys():
            print('  <weather>',file=outfile)
            print('    <name>',scenario,'</name>',file=outfile,sep='')
            print('    <title>',conf.scenarios[scenario]['description'],
                  '</title>',file=outfile,sep='')
            print('    <archs>',file=outfile)
            for arch in conf.scenarios[scenario]['archs']:
                print('      <arch>',arch,'</arch>',file=outfile,sep='')
            print('    </archs>',file=outfile)
            print('  </weather>',file=outfile)
        print('</weathers>',file=outfile)
