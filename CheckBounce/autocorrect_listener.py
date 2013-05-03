import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

if ST3:
    import CheckBounce.const as const
    from CheckBounce.spellchecker import SpellChecker
else:
    import const
    from spellchecker import SpellChecker


class CheckBounceCorrectionListener(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not sublime.load_settings("CheckBounce.sublime-settings").get("autocorrect", False):
            return []

        if not (SpellChecker.is_whitelisted(view) and view.settings().get("enable_checkbounce_spelling", True)):
            return []

        vid = view.id()
        if not const.spell_checkers.get(vid, None):
            return []

        pt = locations[0] - len(prefix)
        loc = sublime.Region(pt, locations[0])

        sugg = const.spell_checkers[vid].suggest(loc)
        if not sugg:
            return []

        completion_list = []
        for suggestion in sugg:
            completion_list += [("{0}\tSuggestion".format(suggestion), suggestion)]

        return (completion_list, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)
