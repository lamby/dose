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

def index_of_percentage(percentage):
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

def icon_of_percentage(percentage):
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
    index=index_of_percentage(percentage)
    return('<img src="../../weathericons/{i}" alt="{t} ({p}%)">'.format(
            i=icon[index],t=text[index],p=percentage))

def percentage(architecture,summary):
    total_packages=summary.get_total(architecture)
    broken_packages=summary.get_broken(architecture)
    if total_packages==0:
        percentage=0
    else:
        percentage=100*broken_packages/total_packages
    return(percentage)

def build(timestamp,scenario,architectures,summary):

    for architecture in architectures:
        perc=percentage(architecture,summary)

        # with open_weatherfile(scenario,arch,'w') as outfile:
        #     print(xml_template.format(
        #             scenario=scenario,
        #             description=conf.scenarios[scenario]['description'],
        #             architecture=architecture,
        #             date=datetime.date.fromtimestamp(float(timestamp)),
        #             number_total=total_packages,
        #             number_broken=broken_packages,
        #             weather=index(perc),
        #             summary_url=url_summary(timestamp,scenario,architecture)),
        #           file=outfile)

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
