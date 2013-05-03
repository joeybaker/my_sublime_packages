import sublime
ST3 = int(sublime.version()) >= 3000

import os
import sys
PyObjCPath = os.path.join(os.path.dirname(__file__), "PyObjC")
if not PyObjCPath in sys.path and ST3:
    sys.path.insert(0, PyObjCPath)
from Foundation import *
from AppKit import *

if ST3:
    import CheckBounce.const as const
else:
    import const
    import functools

import re

class GrammarChecker:
    global ST3
    errors = 0
    error_regions = []
    orthography = None
    raw_results = []

    start = 0
    checker = None
    tag = None
    scope = 'entity.name.function'

    callback = None

    def __init__(self, view, callback):
        self.view = view
        self.callback = callback
        self.checker = NSSpellChecker.sharedSpellChecker()
        self.tag = view.settings().get("spell_tag", None) or NSSpellChecker.uniqueSpellDocumentTag()
        view.settings().set("spell_tag", self.tag)

    @classmethod
    def is_whitelisted(cls, view):
        whitelist = sublime.load_settings("CheckBounce.sublime-settings").get("syntax_whitelist")
        for syntax in whitelist:
            if syntax.lower() in view.scope_name(0):
                return (True, syntax)

        return (False, None)

    @classmethod
    def assign(cls, view, callback):
        try:
            vid = view.id()
        except RuntimeError:
            return

        checker = None
        whitelisted, _ = cls.is_whitelisted(view)
        if whitelisted and view.settings().get("enable_checkbounce_grammar"):
            checker = GrammarChecker(view, callback)
            const.grammar_checkers[vid] = checker
            return checker

        cls.remove(vid)

    @classmethod
    def remove(cls, vid):
        if vid in const.grammar_checkers:
            const.grammar_checkers[vid].clear()

            del const.grammar_checkers[vid]

    @classmethod
    def reload(cls):
        for ID, checker in const.grammar_checkers.items():
            callback = checker.callback
            view = checker.view

            checker.clear()
            const.grammar_checkers[ID] = None
            checker = GrammarChecker(checker.view, checker.callback)
            const.grammar_checkers[ID] = checker

            checker.view = view
            text, start = cls.text(checker.view)
            checker.start = start
            checker.callback = callback
            checker.pre_check(text)

            if ST3:
                callback(checker.view, checker)
            else:
                sublime.set_timeout(functools.partial(callback, checker.view, checker), 0)

        return

    @classmethod
    def text(cls, view):
        text = view.substr(sublime.Region(0, view.size()))
        _, syn = cls.is_whitelisted(view)
        if syn and syn.lower == "latex":
            m = re.search(r"(?s)(?<=\\begin\{document\}).+", text, re.S)
            if m:
                start = m.start(0)
            else:
                start = 0
        else:
            start = 0

        return (text, start)

    @classmethod
    def check_view(cls, view_id, text, start, callback):
        if view_id in const.grammar_checkers:
            checker = const.grammar_checkers[view_id]
            checker.start = start
            checker.callback = callback
            checker.pre_check(text)

            if ST3:
                callback(checker.view, checker)
            else:
                sublime.set_timeout(functools.partial(callback, checker.view, checker), 0)

    @classmethod
    def get_view(cls, view_id):
        if view_id in const.grammar_checkers:
            return const.grammar_checkers[view_id].view

    @classmethod
    def get_checker(cls, view_id):
        if view_id in const.grammar_checkers:
            return const.grammar_checkers[view_id]

    def pre_check(self, text):
        self.errors = 0

        if not text: return

        self.check(text)

    def check(self, text):
        c_range = NSRange()
        c_range.location = self.start
        c_range.length = len(text) - self.start

        c_string = NSString.alloc().initWithUTF8String_(text.encode("utf-8"))

        (errs, self.orthography, wc) = \
            self.checker.checkString_range_types_options_inSpellDocumentWithTag_orthography_wordCount_(c_string,
                c_range,
                NSTextCheckingTypeGrammar,
                None,
                self.tag,
                None,
                None)

        regions = []
        for i in range(errs.count()):
            theResult = errs.objectAtIndex_(i)
            if theResult.resultType() == NSTextCheckingTypeGrammar:
                theRange = theResult.range()
                rangeRegion = sublime.Region(theRange.location, theRange.location + theRange.length)
                regions.append(rangeRegion)

        self.errors = len(regions)
        self.error_regions = regions
        self.raw_results = errs

        self.draw()

    def draw(self):
        if ST3:
            flags = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_EMPTY_AS_OVERWRITE
            self.view.add_regions('checkbounce-grammar-error', self.error_regions, self.scope, '', flags)
        else:
            flags = sublime.DRAW_OUTLINED
            sublime.set_timeout(functools.partial(self.view.add_regions, 'checkbounce-grammar-error', self.error_regions, self.scope, '', flags), 0)

    def clear(self):
        if ST3:
            self.view.erase_regions('checkbounce-grammar-error')
        else:
            sublime.set_timeout(functools.partial(self.view.erase_regions, 'checkbounce-grammar-error'), 0)

    def get_explanation_for_region(self, region):
        expl = []
        for result in self.raw_results:
            theRange = result.range()
            rangeRegion = sublime.Region(theRange.location, theRange.location + theRange.length)
            if region == rangeRegion:
                raw_expl = result.grammarDetails()
                expl = []
                for o in raw_expl:
                    e = o.objectForKey_(NSGrammarUserDescription)
                    e = e.replace('.', '')
                    expl.append(e)

        return "; ".join(expl)
