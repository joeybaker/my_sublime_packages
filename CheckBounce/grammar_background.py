import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

import threading
import time

if ST3:
    from CheckBounce.grammarchecker import GrammarChecker
    import CheckBounce.const as const
else:
    from grammarchecker import GrammarChecker
    import const

class CheckBounceGrammarBackground(sublime_plugin.EventListener):
    global ST3

    def __init__(self):
        super(sublime_plugin.EventListener, self).__init__()

        self.loaded = set()
        self.checked = set()
        self.prev_syntax = {}
        self.start = time.time()
        window = sublime.active_window()
        s = sublime.load_settings("CheckBounce.sublime-settings")

        self.on = s.get("check_grammar", True)

        const.grammar_queue.start(self.check)

        if window and self.on:
            self.on_activated(window.active_view())

    def check(self, view_id):
        view = GrammarChecker.get_view(view_id)

        if view is not None:
            text, start = GrammarChecker.text(view)
            args = (view_id, text, start, self.finish)
            threading.Thread(target=GrammarChecker.check_view, args=args).start()

    def finish(self, view, checker):
        errors = 0
        error_regions = []

        errors = checker.errors
        error_regions = checker.error_regions

        vid = view.id()
        const.grammar_errors[vid] = errors
        const.grammar_error_regions[vid] = error_regions

        self.on_selection_modified(view)

    def hit(self, view):
        if not ST3:
            self.check(view.id())

        self.checked.add(view.id())
        if view.size() == 0:
            g = GrammarChecker.get_checker(view.id())
            if g:
                g.clear()
            GrammarChecker.reload()
            sublime.set_timeout(lambda: view.erase_status('checkbounce-grammar'), 0)
            return

        const.grammar_queue.hit(view)

    def check_grammar(self, view, check=False):
        if check and GrammarChecker.assign(view, self.finish) != None:
            self.hit(view)

    def reassign(self, view):
        v = view.settings()
        v.clear_on_change("checkbounce_grammar_monitor")
        on = v.get("enable_checkbounce_grammar")
        vid = view.id()

        if not vid in self.prev_syntax:
            self.prev_syntax[vid] = v.get("syntax")
        elif self.prev_syntax[vid] != v.get("syntax"):
            GrammarChecker.remove(view.id())
            view.erase_status('checkbounce')
            GrammarChecker.assign(view, self.finish)

        if on != self.on:
            self.on = on
            GrammarChecker.remove(view.id())
            sublime.set_timeout(lambda: view.erase_status('checkbounce-grammar'), 0)
            GrammarChecker.assign(view, self.finish)
            GrammarChecker.reload()
            self.on_modified(view)

        if not on:
            GrammarChecker.remove(view.id())
            sublime.set_timeout(lambda: view.erase_status('checkbounce-grammar'), 0)

        v.add_on_change("checkbounce_grammar_monitor", lambda: self.reassign(view))

    def on_modified(self, view):
        self.on_selection_modified(view)
        self.hit(view)

    def on_load(self, view):
        self.on_new(view)

    def on_activated(self, view):
        if not view:
            return

        v = view.settings()
        if not v.has("enable_checkbounce_grammar"):
            default = sublime.load_settings("CheckBounce.sublime-settings").get("check_grammar", True)
            v.set("enable_checkbounce_grammar", default)
        v.add_on_change('checkbounce_grammar_monitor', lambda: self.reassign(view))

        self.check_grammar(view, True)
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
        if not v.has("enable_checkbounce_grammar"):
            default = sublime.load_settings("CheckBounce.sublime-settings").get("check_grammar", True)
            v.set("enable_checkbounce_grammar", default)
        v.add_on_change('checkbounce_grammar_monitor', lambda: self.reassign(view))

        GrammarChecker.assign(view, self.finish)

    def on_selection_modified(self, view):
        vid = view.id()
        if vid in const.grammar_errors:
            gram_regions = const.grammar_error_regions[vid]
            try:
                sel = view.sel()[0]
            except IndexError:
                view.erase_status('checkbounce-grammar')
                return
            for region in gram_regions:
                if sel.intersects(region):
                    c = GrammarChecker.get_checker(vid)
                    if c:
                        expl = c.get_explanation_for_region(region)
                        if expl:
                            view.set_status('checkbounce-grammar', expl)
                            return

            view.erase_status('checkbounce-grammar')
        else:
            view.erase_status('checkbounce-grammar')

    def on_close(self, view):
        vid = view.id()
        view.settings().clear_on_change("checkbounce_grammar_monitor")
        if vid in self.loaded:
            GrammarChecker.remove(vid)
            self.loaded.remove(vid)
