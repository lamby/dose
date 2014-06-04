#!/usr/bin/python

# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import debianbts

umail='treinen@debian.org'
utag='edos-outdated'

openbugs=dict()
buglist=(debianbts.get_usertag(umail,utag))[utag]
statuslist=debianbts.get_status(buglist)
for status in statuslist:
    if not status.done:
        package=status.package
        affects=status.affects
        number=status.bug_num
        if package in openbugs:
            openbugs[package] =+ number
        else:
            openbugs[package]=[number]
        for p in affects:
            if p in openbugs:
                openbugs[p] =+ number
            else:
                openbugs[p]=[number]

print(openbugs)

