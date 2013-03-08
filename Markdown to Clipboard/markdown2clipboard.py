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
	        
class m2b(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        new_buffer = self.window.new_file()
        if view:
            if view.substr(view.sel()[0]):
                contents = view.substr(view.sel()[0])
                message = u"selection converted and copied to new buffer"
            else:
                contents = view.substr(sublime.Region(0, view.size()))
                message = u"converted and copied to new buffer"
            md = markdown2.markdown(contents, extras=['footnotes', 'wiki-tables'])
            new_buffer.set_syntax_file('Packages/HTML/HTML.tmLanguage')
            new_buffer.set_scratch(True)
            new_buffer.set_name("Preview - HTML")
            edit = new_buffer.begin_edit()
            new_buffer.insert(edit, 0, md)
            new_buffer.end_edit(edit)
            sublime.status_message(message)
