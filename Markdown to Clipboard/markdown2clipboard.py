import sublime, sublime_plugin
import markdown2

class m2c(sublime_plugin.WindowCommand):
    def run(self):
		view = self.window.active_view()
		if view:
			contents = view.substr(sublime.Region(0, view.size()))
	        md = markdown2.markdown(contents,extras=['footnotes','wiki-tables'])
	        sublime.set_clipboard(md)