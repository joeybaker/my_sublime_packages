import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

if ST3:
    from CheckBounce.spellchecker import SpellChecker
    from CheckBounce.grammarchecker import GrammarChecker
else:
    from spellchecker import SpellChecker
    from grammarchecker import GrammarChecker


class ToggleCheckBounceSpellingCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        win = sublime.active_window()
        if not win: return
        view = win.active_view()
        if not view:
            return
        v = view.settings()
        v.set("enable_checkbounce_spelling", not v.get("enable_checkbounce_spelling", True))

    def is_checked(self):
        win = sublime.active_window()
        if not win: return False
        view = win.active_view()
        if not view:
            return False
        v = view.settings()
        whitelisted, _ = SpellChecker.is_whitelisted(view)
        return v.get("enable_checkbounce_spelling", True) and whitelisted

    def is_enabled(self):
        win = sublime.active_window()
        if not win: return False
        view = win.active_view()
        if not view:
            return False
        whitelisted, _ = SpellChecker.is_whitelisted(view)
        return whitelisted


class ToggleCheckBounceGrammarCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        win = sublime.active_window()
        if not win: return
        view = win.active_view()
        if not view:
            return
        v = view.settings()
        v.set("enable_checkbounce_grammar", not v.get("enable_checkbounce_grammar", True))

    def is_checked(self):
        win = sublime.active_window()
        if not win: return False
        view = win.active_view()
        if not view:
            return False
        v = view.settings()
        whitelisted, _ = GrammarChecker.is_whitelisted(view)
        return v.get("enable_checkbounce_grammar", True) and whitelisted

    def is_enabled(self):
        win = sublime.active_window()
        if not win: return False
        view = win.active_view()
        if not view:
            return False
        whitelisted, _ = GrammarChecker.is_whitelisted(view)
        return whitelisted
