import sublime
import sublime_plugin

if int(sublime.version()) >= 3000:
    import CheckBounce.const as const
else:
    import const

class CheckContextualCommand(sublime_plugin.TextCommand):
    def is_visible(self):
        checker = const.spell_checkers.get(self.view.id(), None)
        if not checker:
            return False

        error_regions = checker.error_regions
        for selection in self.view.sel():
            for error_region in error_regions:
                if error_region.contains(selection):
                    return True

        return False

    def run(self, edit, action):
        if not action:
            return

        try:
            lc_action = action.lower()
        except AttributeError:
            return

        self.view.run_command("act_on_word", {"action": lc_action})
