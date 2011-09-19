# -*- coding: utf-8 -*-
# module_utils.py - Miscellaneous utilities for use by linter modules.

import os
import subprocess

import sublime


def get_executable(language, default):
    settings = sublime.load_settings('Base File.sublime-settings')
    map = settings.get('sublimelinter_executable_map')

    if map:
        lang = language.lower()

        if lang in map:
            return map[lang]

    return default


def get_startupinfo():
    info = None

    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

    return info


def execute_get_output(args):
    try:
        return subprocess.Popen(args, get_startupinfo()).communicate()[0]
    except:
        return ''
