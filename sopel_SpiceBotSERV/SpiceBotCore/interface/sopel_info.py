# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import sopel

import requests
import re
from collections import namedtuple


class Sopel_info():
    def __init__(self):

        # local Sopel Version Info
        self.version_local = sopel.version_info
        self.version_local_num = sopel.__version__

        # Online Sopel Version Info
        self.version_url = 'https://sopel.chat/latest.json'
        self.version_online = None
        self.version_online_num = None
        self.releasenotes = None
        self.check_sopel()

    def check_sopel(self):
        info = requests.get(self.version_url).json()
        if self.version_local.releaselevel == 'final':
            self.version_online_num = info['version']
            self.releasenotes = info['release_notes']
        else:
            self.version_online_num = info['unstable']
            self.releasenotes = info.get('unstable_notes', '')
            if self.releasenotes:
                self.releasenotes = 'Full release notes at ' + self.releasenotes

        self.version_online = self._version_info(self.version_online_num)

    def _version_info(self, version):
        regex = re.compile(r'(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?.*')
        version_groups = regex.match(version).groups()
        major, minor, micro = (int(piece) for piece in version_groups[0:3])
        level = version_groups[3]
        serial = int(version_groups[4] or 0)
        if level == 'a':
            level = 'alpha'
        elif level == 'b':
            level = 'beta'
        elif level == 'rc':
            level = 'candidate'
        elif not level and version_groups[4] is None:
            level = 'final'
        else:
            level = 'alpha'
        version_type = namedtuple('version_info',
                                  'major, minor, micro, releaselevel, serial')
        return version_type(major, minor, micro, level, serial)


sopel_info = Sopel_info()
