#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libraries
from __future__ import with_statement

import sys
import glob
import os
import pprint
import cgi
import re
import pyclbr
import inspect

from contextlib import contextmanager

from os.path import ( split, splitext, join, normpath, abspath, isdir,
                      basename, dirname )

# 3rd Party Libs
from lxml.etree import parse

# Sublime Modules
import sublime
import sublimeplugin

# Sublime plugin helpers
from sublimeplugin import commandName

from pluginhelpers import (
    threaded, wait_until_loaded, asset_path, do_in, select,
    #contextual_packages_list, get_contextual_packages, glob_packages
    )

from quickpanelcols import format_for_display
from sublimeconstants import LITERAL_SYMBOLIC_BINDING_MAP
from tmscopes import selector_specificity, compare_candidates, normalize_scope
from bindings import new_binding

from scheduler import scheduled, wait_on_virtual_view

################################### SETTINGS ###################################

CREATE_FILES_FOR = ('sublime-keymap', 'sublime-options')

################################### CONSTANTS ##################################

SUBLIME_KEYMAP = """
<!--
Bindable keys are:
(a-z, 0-9, f1-f15)

backquote, backslash, backspace, browser_back, browser_favorites,
browser_forward, browser_home, browser_refresh, browser_search, browser_stop,
capslock, clear, comma, contextmenu, delete, down, end, enter, equals, escape,
home, insert, left, leftalt, leftbracket, leftcontrol, leftmeta, leftshift,
leftsuper, minus, numlock, pagedown, pageup, pause, period, printscreen, quote,
right, rightalt, rightbracket, rightsuper, scrolllock, semicolon, slash, space,
tab, up

Available modifiers are ctrl, alt, shift.

Lines of the form "key1,key2 bind" will trigger when key1 is pressed, then key2
is pressed.

For example:
<binding key="ctrl+x,ctrl+s" command="save"/>


New key bindings take effect as soon as you save this file, there's no need to
restart Sublime Text.

Also note that if the same key is bound twice, the last binding takes precedence
-->

<bindings>

</bindings>
"""

################################### FUNCTIONS ##################################

def parse_keymap(f):
    root = parse(f).getroot()
    bindings = root.xpath('binding')

    for binding in bindings:
        key = binding.get('key')
        command = binding.get('command')

        scope = binding.xpath('context[@name="selector"][1]/@value')

        # print binding.xpath('context/@name')

        if scope:
            scope = scope[0]
        else:
            scope = 'source,plain'

        yield key, command, scope, binding.sourceline


def normalize_tabtriggers(key):
    if key.endswith(',tab'):
        key = ''.join(key[:-4].split(',')) + '<tab>'

    return key

def normalize_modifier_sequencing(key):
    rebuilt_key = []

    for combo in key.split(','): # TODO: Regex bindings a,b,c,/de,/
        keys = combo.split('+')
        rebuilt_combo = []

        for mod in ('ctrl', 'alt', 'shift'):
            if mod in keys:
                rebuilt_combo.append(keys.pop(keys.index(mod)))

        rebuilt_combo.extend(keys)
        rebuilt_key.append('+'.join(rebuilt_combo))

    return ','.join(rebuilt_key)


def normalize_binding_display(key):
    return normalize_tabtriggers(normalize_modifier_sequencing(key))

################################################################################

def contextual_packages_list(view=None):
    if view is None:
        view = sublime.activeWindow().activeView()

    contextual = get_contextual_packages(view)
    pkg_path = sublime.packagesPath()

    others = sorted((f for f in os.listdir(pkg_path) if isdir(join(pkg_path, f))
                       and not f in contextual), key = lambda f: f.lower())

    return contextual + others

def get_contextual_packages(view):
    try: fn = view.fileName()
    except: return []

    pkg_path = sublime.packagesPath()
    dirs = []

    if fn and normpath(fn).startswith(normpath(pkg_path)):
        dirs.append(split(fn[len(pkg_path)+1:])[0])

    dirs.append(split(split(view.options().get("syntax"))[0])[1])

    return dirs

def glob_packages(file_type='sublime-keymap', view=None):
    pkg_path = sublime.packagesPath()

    for pkg in contextual_packages_list(view):
        path_joins = [pkg_path, pkg, '*.%s' % file_type]
        if pkg == 'Default' and file_type == 'sublime-options':
            path_joins.insert(2, 'Options')

        found_files = glob.glob(join(*path_joins))

        if not found_files and file_type in CREATE_FILES_FOR:
            found_files.append ( join (
                pkg_path, pkg , "%s.%s" % (
                ( sublime.options().get('keymap') if
                  file_type == 'sublime-keymap' else pkg ),
                file_type)
            ))

        for f in found_files:
            yield pkg, splitext(basename(f))[0], f

################################################################################

def open_preference(f, window):
    if not os.path.exists(f):
        if f.endswith('sublime-keymap'):
            to_write = SUBLIME_KEYMAP

        elif f.endswith('sublime-options'):
            to_write = '# sublime-options'
        else:
            to_write = None

        if splitext(f)[1][1:] in CREATE_FILES_FOR and to_write:
            with open(f, 'w') as fh:
                fh.write(to_write)

    return window.openFile(f)


############################### EDIT WITH SYNTAX ###############################

@contextmanager
def editing_lock(view):
    try:
        view.setReadOnly(True)
        yield
    finally:
        view.setReadOnly(False)

def asset_quick_panel(window, asset_type='tmLanguage', full_path=False):
    ftypes = list(glob_packages(asset_type))

    asset = ftypes [( yield
         window.quick_panel(format_for_display(ftypes, cols=(0,1))))[0]][2]

    yield asset if full_path else asset_path(asset)

class EditRegionWithSyntax(sublimeplugin.TextCommand):
    def isEnabled(self, view, args):
        return len(view.sel()) == 1 and not view.isReadOnly()

    @scheduled(every=None)
    def run(self, view, args):
        # TODO: addRegions ... remember the syntax

        sel = view.sel()[0]

        if 'expandSelection' in args:
            sel = view.line(sel)
            view.sel().add(sel)

        window = view.window()
        syntax = (yield asset_quick_panel(window, 'tmLanguage'))

        with editing_lock(view):
            scratch = ( yield wait_on_virtual_view ( window,
                        title   =  "Edit With Syntax",
                        buf     =  view.substr(sel),
                        syntax  =  syntax ) )

        view.replace(sel, scratch.buffer)

#################################### PLUGINS ###################################

class EditPackageFiles(sublimeplugin.WindowCommand):
    def run(self, window, args):
        pref_type = args[0]
        files = list(glob_packages(pref_type))
        keymap = sublime.options().get('keymap')

        if pref_type == 'sublime-keymap':
            display = [(
                (' + ' if not os.path.exists(f[2]) else ' '),
                f[0],
                f[1] if f[1] != keymap else ' ')
                for f in files ]
        else:
            display = [
                ((' + ' if not os.path.exists(f[2]) else ' '),

                f[0],
                f[1] if f[0] != f[1] else ' ')
                for f in files ]

        if all(r[0] == ' ' for r in display):
            display = [r[1:] for r in display]

        display = format_for_display(display)

        sublime.statusMessage (
        'Please choose %s file to %s' % (args[0], ' '.join(args[1:]) or 'edit'))

        def onSelect(i):
            f = files[i][2]

            if len(args) == 1:
                pv = open_preference( f, window)
            else:
                cmd = args[1]
                cmd_args = args[2:] + [asset_path(f)]

                sublime.activeWindow().activeView().runCommand(cmd, cmd_args )

        def onCancel(): pass

        window.showSelectPanel(display, onSelect, onCancel,
          sublime.SELECT_PANEL_MULTI_SELECT, "", 0)


###################### LIST SHORTCUT KEYS COMMANDS OPTIONS #####################

class ListShortcutKeysCommand(sublimeplugin.WindowCommand):
    def run(self, window, args):
        args = []

        keymaps = glob_packages('sublime-keymap')

        for pkg, name, f in keymaps:
            if pkg == 'ZZZ': continue

            if not os.path.exists(f): continue
            try:
                for key, command, scope, line in parse_keymap(f):
                    nkey = normalize_binding_display(key)
                    args.append((pkg, f, key, nkey, command, line, scope))

            except Exception, e:
                print e, f

        view = window.activeView()
        if view:
            scope = normalize_scope( view.syntaxName(
                                     view.sel()[0].begin() ))
            args = sorted (
                args,
                key = lambda t: selector_specificity(t[-1], scope ),
                cmp = compare_candidates,
                reverse = True )

        def onSelect(i):
            f, key, nkey, command, line, scope = args[i][1:7]

            @wait_until_loaded(f)
            def and_then(view):
                regions = [view.line( view.textPoint(int(line)-1, 0) -1 )]

                for search in (key, ):
                    search = cgi.escape(search)
                    new_reg = view.find (
                            search, view.line(regions[-1]).begin(),
                            sublime.LITERAL )

                    if new_reg:
                        regions.append (new_reg)
                    else:
                        break

                for region in regions[-1:]:
                    select(view, region)


        if 'cheatsheet' in args:
            sublime.setClipboard ( '<table>\n\t%s\n</table>' % '\n'.join (
                ("""
                 <tr>
                     <td style='max-width:250px'>%s</td>
                     <td style='max-width:250px;overflow-x: hidden;'>%s</td>
                     <td style=''>%s</td>
                 </tr>
                 """ % tuple (
                    list(cgi.escape(row[i]) for i in (0, 3, 4)))) for row in args ))

        display = format_for_display(args, cols = (0, 3, 4))


        # from quickpanelpp import _quick_panel
        # _quick_panel(window,display, onSelect, None, 0, "", 0)


        window.showSelectPanel(display, onSelect, None, 0, "", 0)

################################################################################

class ListOptions(sublimeplugin.WindowCommand):
    def run(self, window, args):
        options = []

        for pkg, name, f in glob_packages('sublime-options'):
            if not os.path.exists(f): continue
            pkg_display = "%s - %s" % (pkg, name) if name != pkg else pkg
            with open(f) as fh:
                for i, line in enumerate(fh):
                    if line.strip() and not line.startswith('#'):
                        options.append (
                            (pkg_display, line.strip(), f, i + 1) )

        display = format_for_display(options, cols= (0, 1) )

        def onSelect(i):
            window.openFile(*options[i][-2:])

        window.showSelectPanel(display, onSelect, None, 0, "", 0)

################################################################################

class UpdateSnippets(sublimeplugin.WindowCommand):  # HACK LOLOLOLOL
    @scheduled()
    def run(self, window, args):
        from snippets import update_snippet_and_keymap
        from snippets import pretty_dump_xml

        et = None

        for pkg, __, snippet in glob_packages('sublime-snippet'):
            if pkg != 'jQuery': # arged by ctrl+alt+shift+g
                continue

            view = ( yield window.load_file(snippet) )
            print snippet

            et, keymap = update_snippet_and_keymap(view, bulk=True, et=et)
        
        pretty_dump_xml(et, keymap)

class InsertBindingRepr(sublimeplugin.TextCommand):
    def run(self, view, (insertion, )):
        start_pt = view.sel()[0].begin() + len(insertion)
        view.runCommand('insertAndDecodeCharacters', [insertion])

        @do_in(0)
        def l8r():
            binding_region = sublime.Region(start_pt, view.sel()[0].begin() )
            binding = view.substr( binding_region )

            view.erase ( binding_region)
            view.runCommand('insertAndDecodeCharacters',
                [LITERAL_SYMBOLIC_BINDING_MAP.get(binding, binding)]
            )

class CreatePlugin(sublimeplugin.TextCommand):
    @scheduled(every=0)
    def run(self, view, args):
        window = view.window()
        pkgs = contextual_packages_list(view)

        pkg = pkgs[(yield window.quick_panel(pkgs))[0]]
        plugname = yield window.input('Plugin File')

        if not plugname.endswith('.py'): plugname += '.py'
        plugname = join(sublime.packagesPath(), pkg, plugname)

        if not os.path.exists(plugname):
            with open(plugname, 'w') as fh: pass

        plugin = yield window.load_file(plugname)
        plugin.runCommand (
            "insertSnippet 'Packages/Python/sublime-new-plugin-module.sublime-snippet'"
        )

class CreatePluginBinding(sublimeplugin.TextCommand):
    def run(self, view, args):
        plugname = commandName( view.substr(view.word(view.sel()[0])))
        binding = new_binding(command=plugname)
        view.cb = binding

class InsertUUID(sublimeplugin.TextCommand):
    def run(self, view, args):
        from bindings import makeuuid
        view.cmd.insertInlineSnippet(str(makeuuid()))

class NewKeyMapSnippet(sublimeplugin.TextCommand):
    def run(self, view, args):
        view.cmd.insertInlineSnippet(new_binding(key='$1', command='$2'))

################################################################################

class ListCommands(sublimeplugin.WindowCommand):
    "Requires patch to sublimeplugin.py"
    def run(self, window, args):
        commands = []

        the_cmds = zip (
            ('Application', 'Window', 'Text'), sublimeplugin.allCommands )

        the_cmds.extend(sublimeplugin.allCallbacks.items())

        for cmd_type, cmds in the_cmds:
            if type(cmds) is list:
                cmds = dict(
                (sublimeplugin.commandName(type(t).__name__), t) for t in cmds)

            for cmd_name, cmd in cmds.items():
                cmd = type(cmd)

                f = os.path.normpath(inspect.getsourcefile(cmd))
                pkg = f.split('\\')[len(sublime.packagesPath().split('\\'))]

                commands += [(
                    (cmd_type, pkg, cmd_name),
                    f,
                    cmd
                )]

        commands.sort(key=lambda i:i[0])
        display = ['/'.join(i[0]) for i in commands]

        def on_select(i):
            cmd = commands[i]
            cmd_type = cmd[0][0]

            obj = (
                getattr(cmd[-1], cmd_type) if
                cmd_type in sublimeplugin.allCallbacks else cmd[-1] )

            window.openFile(cmd[1], inspect.getsourcelines(obj)[-1])

        window.showSelectPanel(display, on_select, None, 2 | 1, "", 0)

################################################################################