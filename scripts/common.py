# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
import conf

from datetime import date

verbose=True

def info(message):
    if verbose: print(message)

def warning(message):
    print(message)

def cachedir(timestamp,scenario,arch):
    '''
    absolute path of a cache directory for given timestamp, scenario, arch
    '''
    return('{r}/{t}/{s}/{a}'.format(
            r=conf.locations['cacheroot'],
            t=timestamp,
            s=scenario,
            a=arch))

def history_cachedir(scenario):
    return('{r}/history/{s}'.format(
            r=conf.locations['cacheroot'],
            s=scenario))

def history_cachefile(scenario,architecture):
    return('{r}/history/{s}/{a}'.format(
            r=conf.locations['cacheroot'],
            s=scenario,
            a=architecture))

def history_verticalfile(scenario,architecture):
    return('{r}/history/{s}/{a}-perslice'.format(
            r=conf.locations['cacheroot'],
            s=scenario,
            a=architecture))

def history_htmldir(scenario,architecture):
    return('{r}/{s}/history/{a}'.format(
            r=conf.locations['htmlroot'],
            s=scenario,
            a=architecture))

def history_htmlfile(scenario,architecture,days):
    return('{r}/{s}/history/{a}/{d}.html'.format(
            r=conf.locations['htmlroot'],
            s=scenario,
            a=architecture,
            d=days))

def htmldir(timestamp,scenario):
    '''
    absolute path of a html directory for given timestamp, scenario
    '''
    return('{r}/{s}/{t}'.format(
            r=conf.locations['htmlroot'],
            t=timestamp,
            s=scenario))

def htmldir_scenario(scenario):
    '''
    absolute path of a html directory for given scenario
    '''
    return('{r}/{s}'.format(
            r=conf.locations['htmlroot'],
            s=scenario))

def open_weatherfile(scenario,architecture,flags):
    '''
    open the xml file where the "weather data" is stored
    '''
    weatherdir='{r}/results/{s}/latest/{a}'.format(
            r=conf.locations['htmlroot'],
            s=scenario,
            a=architecture)
    weatherfile=weatherdir+'/weather.xml'
    os.makedirs(weatherdir,exist_ok=True)
    return(open(weatherfile, flags))

def open_weather_available_file(flags):
    '''
    open the xml file where available scenarios and archs are announced.
    '''
    weatherdir='{r}/results'.format(
            r=conf.locations['htmlroot'])
    os.makedirs(weatherdir,exist_ok=True)
    weatherfile=weatherdir+'/available.xml'
    return(open(weatherfile, flags))

def pack_anchor(timestamp,package,hash):
    '''
    relative path, from an architecture page, to a package page 
    '''
    return('<a href="../{t}/packages/{p}.html#{h}">'.format(
            t=timestamp,
            p=package,
            h=hash))

def pack_anchor_from_hist(timestamp,package,hash):
    '''
    relative path, from an architecture page, to a package page 
    '''
    return('<a href="../../{t}/packages/{p}.html#{h}">'.format(
            t=timestamp,p=package,
            h=hash))

def url_summary(timestamp,scenario,architecture):
    '''
    url of the summary page for given scenario, time, and architecture.
    '''
    return('http://qa.debian.org/dose/debcheck/{s}/{t}/{a}.html'.format(
            s=scenario,
            t=timestamp,
            a=architecture))

def str_of_list(liste):
    if not liste: return ''
    result, *rest = liste
    for element in rest:
        result += ', ' + element
    return(result)

# number of lines in a file
def lines_in_file(filename):
    return(sum(1 for line in open(filename)))

############################################################################

seconds_per_day = 60 * 60 * 24

def days_since_epoch(time):
    return(time//seconds_per_day)

# ordinal number of 1/1/1970, where 1 = 1/1/0000 
proleptic_of_epoch = 719163

# date corresponding to a number of days since epoch
def date_of_days(days):
    return (date.fromordinal(days+proleptic_of_epoch)).isoformat()

###########################################################################

class bicounter:
    'pair of integer-valued counters'

    c_true = 0
    c_false = 0

    def incr(self,flag):
        'increment the counter indicated by the boolean flag.'

        if flag:
            self.c_true += 1
        else:
            self.c_false += 1

    def __str__(self):
        'return string representation'

        return(str(self.c_true)+'/'+str(self.c_false))

    def total(self):
        'return sum of both counters'

        return(self.c_true + self.c_false)


class bicounter_multi(bicounter):
    ''''
    pair of integer-valued counters. Selection of the counter to be
    incremented uses a dictionary, the values of which are dictionaries
    containing the key "isnative". If one them is true then the counter
    "true" is incremented, otherwise the counter "false" is incremented.
    '''

    def incr(self,d):
        'increment the counter as indicated by the dictionary d.'
        
        flag=False
        for r in d.values():
            if r['isnative']:
                flag=True
                break
        bicounter.incr(self,flag)
