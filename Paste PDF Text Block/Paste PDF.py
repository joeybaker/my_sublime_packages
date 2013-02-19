# coding=utf8
import sublime_plugin, sublime, re

# to transfer cleaned data to sublime text
def clean_paste():
	# step 1. make smart ticks dumb
	data = unicode(sublime.get_clipboard())
	data = data.replace(u'”', '"').replace(u'“', '"').replace(u'’', "'")
	# step 2. replace hr's with new lines
	data = data.replace('________________________________________', '\n')
	# step 3. clean new lines
	data = data.replace('\n', ' ')
	# step 4. watch for multiple spaces
	data = data.replace('    ', ' ') # 4 spaces
	data = data.replace('   ', ' ') # 3 spaces
	data = data.replace('  ', ' ') # 2 spaces
	# step 5. clean previously hyphenated words
	#         this may need a regex to clean scenario
	#         where the text is in form ' - ' & ensure
	#         we are within a few characters of a previous
	#         end line. Table that for now.
	data = data.replace('- ', '') 
	return data;

# to transfer cleaned data and put in double quotes with a footnote prepared in Pandoc notation.
def pandoc_clean_paste():
	paste_block = clean_paste()
	data = "> \"" + paste_block + "\"^[]"
	return data;

# Paste PDF Function
class PastePdf(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(clean_paste())
		self.view.run_command('paste')

class PastePdfPandoc(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(pandoc_clean_paste())
		self.view.run_command('paste')
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		target = self.view.text_point(row, col-1)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(target))
		self.view.show(target)