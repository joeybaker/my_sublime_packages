import os
import re
import json
import sublime
import sublime_plugin


class JSONLintCommand(sublime_plugin.EventListener):

    TIMEOUT_MS = 200
    matcher = re.compile('line (\d+) column')

    def __init__(self):
        self.pending = 0

    def on_modified(self, view):
        syntax = view.settings().get('syntax')
        syntax = os.path.basename(syntax).replace('.tmLanguage', '').lower() if syntax != None else ''
        if syntax != 'json':
            return
        self.pending = self.pending + 1
        sublime.set_timeout(lambda: self.parse(view), self.TIMEOUT_MS)

    def parse(self, view):
        self.pending = self.pending - 1
        if self.pending > 0:
            return

        view.erase_regions('json')
        try:
            json.loads(view.substr(sublime.Region(0, view.size())))
        except ValueError, e:
            message = str(e)
            m = self.matcher.search(message)
            if m:
                row = int(m.group(1)) - 1
                regions = [view.full_line(view.text_point(row, 0)), ]
                view.add_regions('json', regions, 'invalid', 'dot', sublime.DRAW_OUTLINED)
                view.set_status('json', message)
