#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os

from dialogs import launch_gui


def run(bk):
    # before Sigil 0.8.900 and plugin launcher 20150909, bk.selected_iter doesn't exist.
    if bk.launcher_version() < 20150909:
        print('Error: The %s plugin requires Sigil version 0.8.900 or higher.' % bk._w.plugin_name)
        return -1
    
    prefs = bk.getPrefs()
    
    launch_gui(bk, prefs)
    
    bk.savePrefs(prefs)
    
    return 0


def main():
    return -1


if __name__ == "__main__":
    sys.exit(main())
