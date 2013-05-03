import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

if ST3:
    from CheckBounce.spellchecker import SpellChecker
    import CheckBounce.const as const
else:
    from spellchecker import SpellChecker
    import const

class ActOnWordCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        whitelisted, _ = SpellChecker.is_whitelisted(self.view)
        return whitelisted

    def run(self, edit, action=None):
        self.checker = const.spell_checkers.get(self.view.id(), None)
        if not self.checker:
            sublime.status_message("Document has not been spellchecked.")
            return

        if not action:
            action = "summary"

        selected = self.view.sel()
        for selection in selected:
            for error in self.checker.error_regions:
                if error.contains(selection):
                    self.view.sel().add(error)
                    self.word = self.view.substr(error)
                    if action == "ignore":
                        self.checker.ignore_word(self.word)
                        return
                    elif action == "learn":
                        self.checker.learn_word(self.word)
                        return
                    elif action == "suggest" or action == "summary":
                        self.suggest(error)
                        return

        sublime.status_message("Nothing misspelled here.")

    def suggest(self, selection):
        self.corrs = []
        if self.checker.orthography.dominantLanguage() != "und":
            all_corrs = self.checker.suggest(selection)
        else:
            sublime.status_message("Language could not be determined.")
            return

        if all_corrs:
            self.corrs.append(u"\u2766\tIgnore Word")
            self.corrs.append(u"\u2766\tAdd Word to Dictionary")
            for corr in all_corrs:
                self.corrs.append(corr)
            self.view.window().show_quick_panel(self.corrs, self.correct)
        else:
            self.corrs = None
            options = [u"\u2766\tIgnore Word", u"\u2766\tAdd Word to Dictionary", u"\u2767\tNo Suggestions"]
            self.view.window().show_quick_panel(options, self.correct)

    def correct(self, index):
        if index < 0: return
        if index == 0:
            self.checker.ignore_word(self.word)
        elif index == 1:
            self.checker.learn_word(self.word)
        elif index > 1 and self.corrs:
            self.view.run_command("check_bounce_replace", {"replacement": self.corrs[index]})
        else:
            return


class CheckBounceReplaceCommand(sublime_plugin.TextCommand):
    global ST3

    def run(self, edit, replacement, a=None, b=None):
        if a and b and not ST3:
            region = sublime.Region(long(a), long(b))
        elif a and b:
            region = sublime.Region(a, b)
        else:
            region = self.view.sel()[0]

        self.view.replace(edit, region, replacement)
