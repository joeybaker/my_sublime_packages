#
# History:
#
# 2013-03-09:
#    - 
#
# 2013-03-08:
#    - Initial release
#

import os
import re
import sublime
import sublime_plugin

OUTPUT_VIEW_NAME = "debugkiller_result_view"

class DebugKillerCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.view = self.window.active_view()
		self.filePath = self.view.file_name()
		self.fileName = os.path.basename(self.filePath)
		self.scope = self.view.syntax_name(self.view.sel()[0].b).strip().split(" ")

		self.settings = sublime.load_settings("DebugKiller.sublime-settings")
		self.projectSettings = self.view.settings().get("sublime-debugkiller")

		self.allPatterns = self.settings.get("patterns")
		self.patterns = []

		if self.projectSettings:
			print "Project settings found. Loading %s pattern(s)..." % len(self.projectSettings["patterns"])

			for p in self.projectSettings["patterns"]:
				self.allPatterns.append(p)

		#
		# Filter our patterns by our scope
		#
		for p in self.allPatterns:
			for s in p["scopes"]:
				if s in self.scope:
					self.patterns.append(p)
					break

		print ""
		print "All patterns: %s" % self.allPatterns
		print "Scope: %s" % self.scope
		print "Patterns: %s" % self.patterns
		print ""

		#
		# Configure the output view, perform operation search and destroy
		#
		self.configureOutputView()
		self.searchAndDestroy(self.filePath)
		self.showView()

	def searchAndDestroy(self, file):
		print "Debug Killer initializing %s directive%s..." % (len(self.patterns), "s" if len(self.patterns) > 1 else "")
		self.writeToView("Debug Killer initializing %s directives...\n\n" % len(self.patterns))

		lineNum = 0
		f = open(file, "r")

		#
		# Search each line for patterns of items we wish to target 
		#
		for line in f:
			lineNum += 1

			for pattern in self.patterns:
				for match in re.finditer(pattern["pattern"], line, re.IGNORECASE):
					msg = "Target found: %s:%s : %s" % (lineNum, match.start(), match.group(0))
					self.writeToView(msg + "\n")

		f.close()
		self.writeToView("\n>> Objective complete. Click on the items above to highlight the located line\n")

	def configureOutputView(self):
		if not hasattr(self, "outputView"):
			self.outputView = self.window.get_output_panel(OUTPUT_VIEW_NAME)
			self.outputView.set_name(OUTPUT_VIEW_NAME)

		self.clearView()
		self.outputView.settings().set("file_path", self.filePath)

	def clearView(self):
		self.outputView.set_read_only(False)

		edit = self.outputView.begin_edit()
		self.outputView.erase(edit, sublime.Region(0, self.outputView.size()))
		self.outputView.end_edit(edit)
		self.outputView.set_read_only(True)

	def writeToView(self, msg):
		self.outputView.set_read_only(False)

		edit = self.outputView.begin_edit()
		self.outputView.insert(edit, self.outputView.size(), msg)

		self.outputView.end_edit(edit)
		self.outputView.set_read_only(True)

	def showView(self):
		self.window.run_command("show_panel", { "panel": "output." + OUTPUT_VIEW_NAME })


class FindConsoleLogEventListener(sublime_plugin.EventListener):
	disabled = False

	def __init__(self):
		self.previousInstance = None
		self.fileView = None

	def on_selection_modified(self, view):
		if FindConsoleLogEventListener.disabled:
			return

		if view.name() != OUTPUT_VIEW_NAME:
			return

		region = view.line(view.sel()[0])

		#
		# Make sure call once.
		#
		if self.previousInstance == region:
			return

		self.previousInstance = region

		#
		# Extract line from console result.
		#
		text = view.substr(region).split(":")
		if len(text) < 3:
			return

		#
		# Highlight the selected line
		#
		line = text[1].strip()
		col = text[2].strip()
		view.add_regions(OUTPUT_VIEW_NAME, [ region ], "comment")

		#
		# Find the file view.
		#
		filePath = view.settings().get("file_path")
		window = sublime.active_window()
		fileView = None

		for v in window.views():
			if v.file_name() == filePath:
				fileView = v
				break
		
		if fileView == None:
			return

		self.fileView = fileView
		window.focus_view(fileView)
		fileView.run_command("goto_line", {"line": line})
		fileRegion = fileView.line(fileView.sel()[0])

		#
		# Highlight fileView line
		#
		fileView.add_regions(OUTPUT_VIEW_NAME, [ fileRegion ], "string")

	def on_deactivated(self, view):
		if view.name() != OUTPUT_VIEW_NAME:
			return

		self.previousInstance = None

		if self.fileView:
			self.fileView.erase_regions(OUTPUT_VIEW_NAME)
