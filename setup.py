#!/usr/bin/env python

import glob, os 
from distutils.core import setup

install_data = [('share/applications', ['data/com.github.suburbanfilth.noted.desktop']),
                ('share/metainfo', ['data/com.github.suburbanfilth.noted.appdata.xml'])]

setup(  name='com.github.suburbanfilth.noted',
        version='1.0.0',
        author='Martin Spasov',
        description='Take notes with ease',
        url='https://github.com/SuburbanFilth/Noted',
        license='GNU GPL2',
        scripts=['com.github.suburbanfilth.noted'],
        packages=['noted'],
        data_files=install_data)
