# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function

import sopel

import requests


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
        info = requests.get(self.sopel["version_url"]).json()
        if self.version_local.releaselevel == 'final':
            self.version_online_num = info['version']
            self.releasenotes = info['release_notes']
        else:
            self.version_online_num = info['unstable']
            self.releasenotes = info.get('unstable_notes', '')
            if self.releasenotes:
                self.releasenotes = 'Full release notes at ' + self.releasenotes

        self.version_online = sopel._version_info(self.version_online_num)


sopel_info = Sopel_info()
