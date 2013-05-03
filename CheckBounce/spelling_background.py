import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

import threading
import time

if ST3:
    from CheckBounce.spellchecker import SpellChecker
    import CheckBounce.const as const
else:
    from spellchecker import SpellChecker
    import const

class CheckBounceSpellingBackground(sublime_plugin.EventListener):
    global ST3

    def __init__(self):
        super(sublime_plugin.EventListener, self).__init__()

        self.loaded = set()
        self.checked = set()
        self.prev_syntax = {}
        self.start = time.time()
        window = sublime.active_window()
        s = sublime.load_settings("CheckBounce.sublime-settings")

        self.on = s.get("check_spelling", True)

        const.spell_queue.start(self.check)

        if window and self.on:
            self.on_activated(window.active_view())

    def check(self, view_id):
        view = SpellChecker.get_view(view_id)

        if view is not None:
            text, start = SpellChecker.text(view)
            args = (view_id, text, start, self.finish)
            threading.Thread(target=SpellChecker.check_view, args=args).start()

    def finish(self, view, checker):
        errors = 0
        words = 0
        error_regions = []

        errors = checker.errors
        words = checker.words
        error_regions = checker.error_regions

        vid = view.id()
        const.spell_errors[vid] = errors
        const.spell_error_regions[vid] = error_regions
        const.words[vid] = words

        self.on_selection_modified(view)

    def hit(self, view):
        if not ST3:
            self.check(view.id())

        self.checked.add(view.id())
        if view.size() == 0:
            c = SpellChecker.get_checker(view.id())
            if c:
                c.clear()
            SpellChecker.reload()
            sublime.set_timeout(lambda: view.erase_status('checkbounce'), 0)
            return

        const.spell_queue.hit(view)

    def check_spelling(self, view, check=False):
        if check and SpellChecker.assign(view, self.finish) != None:
            self.hit(view)

    def reassign(self, view):
        v = view.settings()
        v.clear_on_change("checkbounce_spelling_monitor")
        on = v.get("enable_checkbounce_spelling")
        vid = view.id()

        if not vid in self.prev_syntax:
            self.prev_syntax[vid] = v.get("syntax")
        elif self.prev_syntax[vid] != v.get("syntax"):
            SpellChecker.remove(view.id())
            view.erase_status('checkbounce')
            SpellChecker.assign(view, self.finish)

        if on != self.on:
            self.on = on
            SpellChecker.remove(vid)
            sublime.set_timeout(lambda: view.erase_status('checkbounce'), 0)

            if on:
                SpellChecker.assign(view, self.finish)
                SpellChecker.reload()
            if not on:
                if vid in self.loaded:
                    self.loaded.remove(vid)
                if vid in self.checked:
                    self.checked.remove(vid)

            self.on_modified(view)

        v.add_on_change('checkbounce_spelling_monitor', lambda: self.reassign(view))

    def on_modified(self, view):
        self.on_selection_modified(view)
        self.hit(view)

    def on_load(self, view):
        self.on_new(view)

    def on_activated(self, view):
        if not view:
            return

        v = view.settings()
        if not v.has("enable_checkbounce_spelling"):
            default = sublime.load_settings("CheckBounce.sublime-settings").get("check_spelling", True)
            v.set("enable_checkbounce_spelling", default)
        v.add_on_change('checkbounce_spelling_monitor', lambda: self.reassign(view))

        self.check_spelling(view, True)
        view_id = view.id()
        if not view_id in self.checked:
            if not view_id in self.loaded:
                if time.time() - self.start < 5: return
                self.on_new(view)

            self.hit(view)

        self.on_selection_modified(view)

    def on_new(self, view):
        vid = view.id()
        self.loaded.add(vid)
        v = view.settings()
        if not v.has("enable_checkbounce_spelling"):
            default = sublime.load_settings("CheckBounce.sublime-settings").get("check_spelling", True)
            v.set("enable_checkbounce_spelling", default)

        v.add_on_change('checkbounce_spelling_monitor', lambda: self.reassign(view))
        SpellChecker.assign(view, self.finish)

    def on_selection_modified(self, view):
        vid = view.id()
        if vid in const.spell_errors:
            words = const.words[vid]
            errors = const.spell_errors[vid]
            word_sib = 's' if words != 1 else ''

            spell_status = "%s word%s, %s misspelled" % (words, word_sib, errors)
            view.set_status('checkbounce', spell_status)
        else:
            view.erase_status('checkbounce')

    def on_close(self, view):
        vid = view.id()
        view.settings().clear_on_change("checkbounce_spelling_monitor")
        if vid in self.loaded:
            SpellChecker.remove(vid)
            self.loaded.remove(vid)
