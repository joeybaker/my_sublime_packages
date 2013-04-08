import sublime, sublime_plugin, os
import re
import subprocess
import threading
import time
from os.path import expanduser

#
# This code is based on the PHPCS tools by 
#    ____  ____  _____ _   _ __  __    _  _____ ____  _____ _     ______   __
#   / __ \| __ )| ____| \ | |  \/  |  / \|_   _/ ___|| ____| |   | __ ) \ / /
#  / / _` |  _ \|  _| |  \| | |\/| | / _ \ | | \___ \|  _| | |   |  _ \\ V / 
# | | (_| | |_) | |___| |\  | |  | |/ ___ \| |  ___) | |___| |___| |_) || |  
#  \ \__,_|____/|_____|_| \_|_|  |_/_/   \_\_| |____/|_____|_____|____/ |_|  
#   \____/                                   https://github.com/benmatselby
#
# In fact I'd go so far as to say I deleted more code than I added to turn this into
# the Puppet syntax checker.
#
# Thanks Ben. <3


class Pref:
    @staticmethod
    def load():
        settings = sublime.load_settings('puppet-syntax.sublime-settings')
        Pref.show_debug = settings.get('show_debug', False)
        Pref.puppet_path = settings.get('puppet_path', '/usr/bin/puppet')
        Pref.puppetsyntax_show_gutter_marks = settings.get('puppetsyntax_show_gutter_marks', True)
        Pref.puppetsyntax_outline_for_errors = settings.get('puppetsyntax_outline_for_errors', True)
        Pref.puppetsyntax_show_errors_on_save = settings.get('puppetsyntax_show_errors_on_save', True)
        Pref.puppetsyntax_show_quick_panel = settings.get('puppetsyntax_show_quick_panel', True)
        Pref.puppetsyntax_additional_args = settings.get('puppetsyntax_additional_args', {})

Pref.load()

def debug_message(msg):
    if Pref.show_debug == True:
        print("[Puppet-Syntax] " + str(msg))



class PuppetError():
    """Represents an error that needs to be displayed on the UI for the user"""
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def get_line(self):
        return self.line

    def get_message(self):
        data = self.message

        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            data = data.decode(sublime.active_window().active_view().settings().get('fallback_encoding'))
        
        return data

    def set_point(self, point):
        self.point = point

    def get_point(self):
        return self.point

class ShellCommand():
    """Base class for shelling out a command to the terminal"""
    def __init__(self):
        self.error_list = []

    def get_errors(self, path):
        self.execute(path)
        return self.error_list

    def shell_out(self, cmd):
        data = None
        debug_message(' '.join(cmd))

        info = None
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE

        home = expanduser("~")
        debug_message("cwd: " + home)

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info, cwd=home)

        if proc.stdout:
            data = proc.communicate()[0]

        return data

    def execute(self, path):
        debug_message('Command not implemented')


class PuppetSyntax(ShellCommand):
    """Concrete class for Puppet"""
    def execute(self, path):
        args = []

        if Pref.puppet_path != "":
            application_path = Pref.puppet_path
        else:
            application_path = 'puppet'

        if (len(args) > 0):
            args.append(application_path)
        else:
            args = [application_path]

        args.append("parser")
        args.append("validate")

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.puppetsyntax_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        args.append(os.path.normpath(path))
        
        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message('Parsing')
        debug_message(report)

        lines = re.finditer('Error: Could not parse.*:(?P<message>.+) at (?P<filename>.+):(?P<line>\d+)', report)

        for line in lines:
            error = PuppetError(line.group('line'), line.group('message'))
            self.error_list.append(error)

class PuppetSyntaxCommand():
    """Main plugin class for building the puppet syntax report"""

    # Class variable, stores the instances.
    instances = {}

    @staticmethod
    def instance(view, allow_new=True):
        '''Return the last-used instance for a given view.'''
        view_id = view.id()
        if view_id not in PuppetSyntaxCommand.instances:
            if not allow_new:
                return False
            PuppetSyntaxCommand.instances[view_id] = PuppetSyntaxCommand(view.window())
        return PuppetSyntaxCommand.instances[view_id]

    def __init__(self, window):
        self.window = window
        self.syntax_reports = []
        self.report = []
        self.event = None
        self.error_lines = {}
        self.error_list = []
        self.shell_commands = ['Puppet']

    def run(self, path, event=None):
        self.event = event
        self.syntax_reports = []
        self.report = []

        if event == 'on_save':
            self.syntax_reports.append(['Puppet', PuppetSyntax().get_errors(path), 'dot'])

        sublime.set_timeout(self.generate, 0)

    def clear_sniffer_marks(self):
        for region in self.shell_commands:
            self.window.active_view().erase_regions(region)

    def set_status_bar(self):
        if self.window.active_view().is_scratch():
            return

        line = self.window.active_view().rowcol(self.window.active_view().sel()[0].end())[0]
        errors = self.get_errors(line)
        if errors:
            self.window.active_view().set_status('PuppetSyntax', errors)
        else:
            self.window.active_view().erase_status('PuppetSyntax')

    def generate(self):
        self.error_list = []
        region_set = []
        self.error_lines = {}

        for shell_command, report, icon in self.syntax_reports:
            self.window.active_view().erase_regions('puppet-syntax')
            self.window.active_view().erase_regions(shell_command)

            debug_message(shell_command + ' found ' + str(len(report)) + ' errors')
            for error in report:
                line = int(error.get_line())
                pt = self.window.active_view().text_point(line - 1, 0)
                region_line = self.window.active_view().line(pt)
                region_set.append(region_line)
                self.error_list.append('(' + str(line) + ') ' + error.get_message())
                error.set_point(pt)
                self.report.append(error)
                self.error_lines[line] = error.get_message()

            if len(self.error_list) > 0:
                icon = icon if Pref.puppetsyntax_show_gutter_marks else ''
                outline = sublime.DRAW_OUTLINED if Pref.puppetsyntax_outline_for_errors else sublime.HIDDEN
                if Pref.puppetsyntax_show_gutter_marks or Pref.puppetsyntax_outline_for_errors:
                    self.window.active_view().add_regions(shell_command,
                        region_set, shell_command, icon, outline)

        if Pref.puppetsyntax_show_quick_panel == True:
            # Skip showing the errors if we ran on save, and the option isn't set.
            if self.event == 'on_save' and not Pref.puppetsyntax_show_errors_on_save:
                return
            self.show_quick_panel()

    def show_quick_panel(self):
        self.window.show_quick_panel(self.error_list, self.on_quick_panel_done)

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        if (len(self.report) > 0):
            pt = self.report[picked].get_point()
            self.window.active_view().sel().clear()
            self.window.active_view().sel().add(sublime.Region(pt))
            self.window.active_view().show(pt)
            self.set_status_bar()

    def get_errors(self, line):
        if not line + 1 in self.error_lines:
            return False

        return self.error_lines[line + 1]

    def get_next_error(self, line):
        current_line = line + 1

        cache_error=None
        # todo: Need a way of getting the line count of the current file!
        cache_line=1000000
        for error in self.report:
            error_line = error.get_line()

            if cache_error != None:
                cache_line = cache_error.get_line()

            if int(error_line) > int(current_line) and int(error_line) < int(cache_line):
                cache_error = error

        if cache_error != None:
            pt = cache_error.get_point()
            self.window.active_view().sel().clear()
            self.window.active_view().sel().add(sublime.Region(pt))
            self.window.active_view().show(pt)


class PhpcsTextBase(sublime_plugin.TextCommand):
    """Base class for Text commands in the plugin, mainly here to check php files"""
    description = ''

    def run(self, args):
        debug_message('Not implemented')

    def description(self):
        if not PhpcsTextBase.should_execute(self.view):
            return "Invalid file format"
        else:
            return self.description

    @staticmethod
    def should_execute(view):
        if view.file_name() != None:
            ext = os.path.splitext(view.file_name())[1]
            result = ext[1:] in Pref.extensions_to_execute
            return result

        return False

class PuppetTextBase(sublime_plugin.TextCommand):
    """Base class for Text commands in the plugin, mainly here to check puppet files"""
    description = ''

    def run(self, args):
        debug_message('Not implemented')

    def description(self):
        if not PhpcsTextBase.should_execute(self.view):
            return "Invalid file format"
        else:
            return self.description

    @staticmethod
    def should_execute(view):
        if view.file_name() != None:
            ext = os.path.splitext(view.file_name())[1]
            result = ext[1:] == 'pp'
            return result

        return False

class PuppetSyntaxEventListener(sublime_plugin.EventListener):
    """Event listener for the plugin"""
    def on_post_save(self, view):
        if PuppetTextBase.should_execute(view):

            cmd = PuppetSyntaxCommand.instance(view)
            thread = threading.Thread(target=cmd.run, args=(view.file_name(), 'on_save'))
            thread.start()