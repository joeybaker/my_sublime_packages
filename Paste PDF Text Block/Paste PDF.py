# coding=utf8
import sublime_plugin, sublime, re

# to transfer cleaned data to sublime text
def clean_paste( data ):
	# step 1. make smart ticks dumb
	# data = unicode(sublime.get_clipboard())
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

	# French accents (Gery Casiez)
	data = data.replace(u'à',u'à')
	data = data.replace(u'â',u'â')
	data = data.replace(u'À',u'À')
	data = data.replace(u'Â',u'Â')

	data = data.replace(u'é',u'é')
	data = data.replace(u'è',u'è')
	data = data.replace(u'ê',u'ê')
	data = data.replace(u'e¨',u'ë')

	data = data.replace(u'É',u'É')
	data = data.replace(u'È',u'È')
	data = data.replace(u'Ê',u'Ê')
	data = data.replace(u'E¨',u'Ë')

	data = data.replace(u'î',u'î')
	data = data.replace(u'Î',u'Î')
	data = data.replace(u'ï',u'ï')
	data = data.replace(u'Ï',u'Ï')

	data = data.replace(u'ô',u'ô')
	data = data.replace(u'Ô',u'Ô')

	data = data.replace(u'ù',u'ù')
	data = data.replace(u'Ù',u'Ù')
	data = data.replace(u'û',u'û')
	data = data.replace(u'Û',u'Û')

	data = data.replace(u'œ',u'\oe ')
	data = data.replace(u'Ç',u'Ç')
	data = data.replace(u'ç',u'ç')

	return data;

# to transfer cleaned data and put in double quotes with a footnote prepared in Pandoc notation.
def pandoc_clean_paste( data ):
	paste_block = clean_paste( data )
	data = "\"" + paste_block + "\"^[]"
	return data;

# Paste PDF Function
class PastePdf(sublime_plugin.TextCommand):
	def run(self, edit):
		old_clipboard = unicode(sublime.get_clipboard())
		sublime.set_clipboard(clean_paste(old_clipboard))
		self.view.run_command('paste')

class PastePdfPandoc(sublime_plugin.TextCommand):
	def run(self, edit):
		old_clipboard = unicode(sublime.get_clipboard())
		sublime.set_clipboard(pandoc_clean_paste(old_clipboard))
		self.view.run_command('paste')
		sublime.set_clipboard(old_clipboard)
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		target = self.view.text_point(row, col-1)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(target))
		self.view.show(target)
