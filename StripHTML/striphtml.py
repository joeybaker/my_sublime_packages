import sublime, sublime_plugin
import re

class StripHtmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sels = self.view.sel()

		for sel in sels:
			selected = self.view.substr(sel)
			strippedText = re.sub('<[^>]*>', '', selected)
			self.view.replace(edit, sel, strippedText)

		self.view.sel().clear()