#!/usr/bin/python3

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import time, os, argparse, re
import conf, universes, reports, horizontal, vertical, cleanup, common, diffs

argparser=argparse.ArgumentParser(
    description="Run dose-debcheck and analyze the result.")
argparser.add_argument('--skip-debcheck',dest='skip_debcheck',
                       action='store_true', required=False,
                       help='Only rebuild tables for the last run.')
arguments=argparser.parse_args()

time_now = int(time.time())
day_now  = common.days_since_epoch(time_now)
timestamp_now = str(time_now)

timestamps_known = [t for t in os.listdir(conf.locations['cacheroot'])
                    if re.match(r'^[0-9]+$', t)]
timestamps_known.sort(reverse=True)
if timestamps_known:
    timestamp_last = timestamps_known[0]
else:
    timestamp_last = None

if arguments.skip_debcheck and not timestamp_last:
    raise Exception('cannot find any previous runs')

if arguments.skip_debcheck and timestamp_last:
    timestamp_this = timestamp_last
    timestamps_keep = timestamps_known[0:conf.slices]
else:
    timestamp_this = timestamp_now
    timestamps_keep = timestamps_known[0:conf.slices-1]
    timestamps_keep[0:0] = [timestamp_now]
            
for scenario in conf.scenarios.keys():
    architectures = conf.scenarios[scenario]['archs']

    if not arguments.skip_debcheck:
        for arch in architectures:
            universes.build(timestamp_this,scenario,arch)

    for arch in architectures:
        reports.build(timestamp_this,day_now,scenario,arch)
        diffs.build(timestamp_this,timestamp_last,scenario,arch)
            
    horizontal.build(timestamp_this,day_now,scenario,architectures)

    vertical.build(timestamps_keep,scenario,architectures)

cleanup.cleanup(timestamps_keep, timestamps_known, timestamp_this, 
                conf.scenarios.keys())




