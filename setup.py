#!/usr/bin/env python

import glob, os 
from distutils.core import setup

install_data = [('share/applications', ['data/com.github.suburbanfilth.noted.desktop']),
                ('share/metainfo', ['data/com.github.suburbanfilth.noted.appdata.xml']),
                ('share/icons/hicolor/32x32/apps',['data/icons/32/com.github.suburbanfilth.noted.png']),
                ('share/icons/hicolor/48x48/apps',['data/icons/48/com.github.suburbanfilth.noted.png']),
                ('share/icons/hicolor/64x64/apps',['data/icons/64/com.github.suburbanfilth.noted.png']),
                ('share/icons/hicolor/128x128/apps',['data/icons/128/com.github.suburbanfilth.noted.png'])]

setup(  name='Noted',
        version='0.1',
        author='Martin Spasov',
        description='Take notes with ease',
        url='https://github.com/SuburbanFilth/noted',
        license='GNU GPL2',
        scripts=['com.github.suburbanfilth.noted'],
        packages=['noted', 'noted/dialogs', 'noted/logger'],
        data_files=install_data)
