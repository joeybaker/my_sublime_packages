# wrap_each
import sublime, sublime_plugin
import re

class WrapEachCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = self.view.sel()
    scope = self.view.scope_name(selection[0].begin())

    if scope.find('text.html.basic') == -1:
      return

    for region in selection:
      if region.empty():
        return

      s = re.sub(r'(?m)^(\s*)(.+?)(\s*)$', '\g<1><li>\g<2></li>\g<3>', self.view.substr(region))

      self.view.replace(edit, region, s)

    start = selection[0].begin()
    selection.clear()

    for i in xrange(0,len(s)):
      if s[i] == '<' and s[i + 1] + s[i + 2] == 'li':
        selection.add(sublime.Region(start + i + 1, start + i + 3))
        i += 2

      elif s[i] == '<' and s[i + 2] + s[i + 3] == 'li':
        selection.add(sublime.Region(start + i + 2, start + i + 4))
        i += 3
