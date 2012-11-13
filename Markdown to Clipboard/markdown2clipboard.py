import sublime, sublime_plugin
import markdown2

class m2c(sublime_plugin.WindowCommand):
    def run(self):
		view = self.window.active_view()
		if view:
			if view.substr(view.sel()[0]):
				contents = view.substr(view.sel()[0])
				message = u"selection converted and copied to clipboard"
			else:
				contents = view.substr(sublime.Region(0, view.size()))
				message = u"converted and copied to clipboard"
	        md = markdown2.markdown(contents,extras=['footnotes','wiki-tables'])
	        sublime.set_clipboard(md)
	        sublime.status_message(message)