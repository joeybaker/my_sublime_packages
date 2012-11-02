import sublime, sublime_plugin
import os, string, re

plugin_directory = os.getcwdu()

class DetectSyntaxCommand(sublime_plugin.EventListener):
	def __init__(self):
		super(DetectSyntaxCommand, self).__init__()
		self.first_line = None
		self.file_name = None
		self.view = None
		self.syntaxes = []
		self.plugin_name = 'DetectSyntax'
		self.plugin_dir = plugin_directory
		self.user_dir = sublime.packages_path() + os.path.sep + 'User'
		self.settings_file = self.plugin_name + '.sublime-settings'
		self.reraise_exceptions = False

		self.ensure_user_settings()


	def on_new(self, view):
		settings = sublime.load_settings(self.settings_file)
		name = settings.get("new_file_syntax")
		if name:
			self.view = view
			self.set_syntax(name)


	def on_load(self, view):
		self.detect_syntax(view)

	
	def on_post_save(self, view):
		self.detect_syntax(view)
	  

	def detect_syntax(self, view):
		if view.is_scratch() or not view.file_name: # buffer has never been saved
			return

		self.reset_cache_variables(view)
		self.load_syntaxes()
		
		if not self.syntaxes:
			return

		for syntax in self.syntaxes:
			# stop on the first syntax that matches
			if self.syntax_matches(syntax):
				self.set_syntax(syntax.get("name"))
				break


	def reset_cache_variables(self, view):
		self.view = view
		self.file_name = view.file_name()
		self.first_line = view.substr(view.line(0))
		self.syntaxes = []
		self.reraise_exceptions = False


	def set_syntax(self, name):
		# the default settings file uses / to separate the syntax name parts, but if the user
		# is on windows, that might not work right. And if the user happens to be on Mac/Linux but
		# is using rules that were written on windows, the same thing will happen. So let's
		# be intelligent about this and replace / and \ with os.path.sep to get to
		# a reasonable starting point
		name = name.replace('/', os.path.sep)
		name = name.replace('\\', os.path.sep)

		dirs = name.split(os.path.sep)
		name = dirs.pop()
		path = os.path.sep.join(dirs)

		if not path:
			path = name

		file_name = name + '.tmLanguage'
		new_syntax = 'Packages/' + path + '/' + file_name
		new_syntax_path = os.path.sep.join([sublime.packages_path(), path, file_name])

		current_syntax = self.view.settings().get('syntax')

		# only set the syntax if it's different
		if new_syntax != current_syntax:
			# let's make sure it exists first!
			if os.path.exists(new_syntax_path):
				self.view.set_syntax_file(new_syntax)
				print 'Syntax set to ' + name + ' using ' + new_syntax_path
			else:
				print 'Syntax file for ' + name + ' does not exist at ' + new_syntax_path


	def load_syntaxes(self):
		settings = sublime.load_settings(self.plugin_name + '.sublime-settings')
		self.reraise_exceptions = settings.get("reraise_exceptions")
		# load the default syntaxes
		default_syntaxes = settings.get("default_syntaxes")
		if default_syntaxes is None:
			default_syntaxes = []
		# load any user-defined syntaxes
		user_syntaxes = settings.get("syntaxes")
		if user_syntaxes is None:
			user_syntaxes = []
		
		self.syntaxes = user_syntaxes + default_syntaxes


	def syntax_matches(self, syntax):
		rules = syntax.get("rules")
		match_all = syntax.get("match") == 'all'

		for rule in rules:
			if 'function' in rule:
				result = self.function_matches(rule)
			else:
				result = self.regexp_matches(rule)

			if match_all:
				# can return on the first failure since they all
				# have to match
				if not result:
					return False
			elif result:
				# return on first match. don't return if it doesn't
				# match or else the remaining rules won't be applied
				return True

		if match_all:
			# if we need to match all and we got here, then all of the
			# rules matched
			return True
		else:
			# if we needed to match just one and got here, none of the
			# rules matched
			return False


	def function_matches(self, rule):
		function = rule.get("function")
		path_to_file = function.get("source")
		function_name = function.get("name")

		if not path_to_file:
			path_to_file = function_name + '.py'

		# is path_to_file absolute?
		if not os.path.isabs(path_to_file):
			user_file = self.user_dir + os.path.sep + path_to_file
			plugin_file = self.plugin_dir + os.path.sep + path_to_file

			# it's not absolute, so look in Packages/User
			if os.path.exists(user_file):
				path_to_file = user_file
			# now look in the plugin's directory
			elif os.path.exists(plugin_file):
				path_to_file = plugin_file
			else:
				# can't find it ... nothing more to do
				return False

		# bubble exceptions up only if the user wants them
		try:
			with open(path_to_file, 'r') as the_file:
				function_source = the_file.read()
		except:
			if self.reraise_exceptions:
				raise
			else:
				return False

		try:
			exec(function_source)
		except:
			if self.reraise_exceptions:
				raise
			else:
				return False

		try:
			return eval(function_name + '(\'' + self.file_name + '\')')
		except:
			if self.reraise_exceptions:
				raise
			else:
				return False


	def regexp_matches(self, rule):
		if "first_line" in rule:
			subject = self.first_line
			regexp = rule.get("first_line")
		elif "binary" in rule:
			subject = self.first_line
			regexp = '^#\\!(?:.+)' + rule.get("binary")
		elif "file_name" in rule:
			subject = self.file_name
			regexp = rule.get("file_name")
		else:
			return False

		if regexp and subject:
			return re.match(regexp, subject) != None
		else:
			return False


	def ensure_user_settings(self):
		user_settings_file = self.user_dir + os.path.sep + self.settings_file
		if os.path.exists(user_settings_file):
			return

		# file doesn't exist, let's create a bare one
		output = """
{
	// If you want exceptions reraised so you can see them in the console, change this to true.
	"reraise_exceptions": false,

	// If you want to have a syntax applied when new files are created, set new_file_syntax to the name of the syntax to use.
	// The format is exactly the same as "name" in the rules below. For example, if you want to have a new file use 
	// JavaScript syntax, set new_file_syntax to 'JavaScript'.
	"new_file_syntax": false,

	// Put your custom syntax rules here:
	"syntaxes": [
	]
}
"""

		file = open(user_settings_file, 'w')
		file.write(output)
		file.close
