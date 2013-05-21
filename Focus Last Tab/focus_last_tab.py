import sublime, sublime_plugin

class LastViewCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        views = window.views_in_group(window.active_group())
        settings = sublime.load_settings("Preferences.sublime-settings")
        if settings.get("focus_last_tab_override", True):
            window.focus_view(views[-1])
        elif len(views) >= 9:
            window.focus_view(views[9])
