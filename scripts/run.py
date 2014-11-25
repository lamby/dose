#!/usr/bin/python3

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import time, os, re
import conf, universes, reports, horizontal, vertical, cleanup, common, diffs, weather, bts

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

timestamps_keep = timestamps_known[0:conf.slices-1]
timestamps_keep[0:0] = [timestamp_now]

bugtable=bts.Bugtable()

for scenario in conf.scenarios:
    summary = horizontal.Summary(scenario,timestamp_now)

    for arch in summary.get_architectures():
        universes.build(timestamp_now,scenario,arch)
        if scenario['type'] == 'binary':
            universe=universes.BinUniverse(timestamp_now,scenario,arch,summary)
        elif scenario['type'] == 'source':
            # FIXME
            universe=universes.BinUniverse(timestamp_now,scenario,arch,summary)
        reports.build(timestamp_now,day_now,universe,scenario['name'],arch,
                      bugtable,summary)
        diffs.build(timestamp_now,timestamp_last,universe,scenario['name'],arch)
        
    horizontal.build(timestamp_now,day_now,scenario['name'],bugtable,summary)
    for what in ['some','each']:
        diffs.build_multi(timestamp_now,timestamp_last,scenario['name'],
                          what,summary)
        
    weather.build(timestamp_now,scenario['name'],summary)
    vertical.build(timestamps_keep,scenario['name'],summary)

    # weather.write_available()    
cleanup.cleanup(timestamps_keep, timestamps_known, timestamp_now, 
                {sc['name'] for sc in conf.scenarios})
