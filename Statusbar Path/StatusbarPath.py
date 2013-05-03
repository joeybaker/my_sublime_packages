import sublime
import sublime_plugin


class CurrentPathStatusCommand(sublime_plugin.EventListener):

    def on_activated(self, view):
        filename = view.file_name()
        if filename:
            view.set_status('zPath', filename)
