# Copyright (C) 2014 Ralf Treinen <treinen@debian.org>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, shutil
import conf

def cleanup(timestamps_keep,timestamps_known,scenarios):

    for directory in timestamps_known:
        if directory not in timestamps_keep:
            shutil.rmtree(cacheroot+'/'+directory)

    htmlroot = conf.locations['htmlroot']
    for directory1 in os.listdir(htmlroot):
        path1=htmlroot+'/'+directory1
        if os.path.isdir(path1):
            if directory1 not in scenarios:
                shutil.rmtree(path1)
            else:
                for directory2 in os.listdir(path1):
                    path2=path1+'/'+directory2
                    if directory2 not in timestamps_keep and os.path.isdir(path2):
                        shutil.rmtree(path2)
            

