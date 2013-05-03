import sublime
import sublime_plugin
ST3 = int(sublime.version()) >= 3000

if ST3:
    import CheckBounce.const as const
    from CheckBounce.spellchecker import SpellChecker
else:
    import const
    from spellchecker import SpellChecker


class CheckBounceCycleCommand(sublime_plugin.TextCommand):
    global ST3

    def is_enabled(self):
        whitelisted, _ = SpellChecker.is_whitelisted(self.view)
        return whitelisted

    def run(self, edit):
        SpellChecker.reload()
        try:
            errs = const.spell_error_regions[self.view.id()]
        except KeyError:
            sublime.status_message("Document has not been checked.")
            return
        errs = sorted(errs, key=lambda e: e.a)
        try:
            self.checker = SpellChecker.get_checker(self.view.id())
        except KeyError:
            sublime.status_message("Document has not been checked.")
            return

        if self.checker.orthography.dominantLanguage() == "und":
            sublime.status_message("Language could not be determined.")
            return
        if not len(errs):
            sublime.status_message("No errors!")
            return

        self.offset = 0
        self.reset = 0
        self.i = 0
        self.forward = True
        self.ignored = []

        pos = self.view.sel()[0].a
        # self.view.sel().clear()
        start = 0
        for j in range(len(errs)):
            if errs[j].contains(pos):
                start = j
                break

            b = errs[j].b
            try:
                x = errs[j + 1].a
            except IndexError:
                break

            if b < pos < x:
                start = j + 1
                break
        self.start = start
        end_chunk = errs[start:]
        beginning_chunk = errs[:start]
        self.chunks = []
        if not beginning_chunk == end_chunk:
            self.chunks.extend(end_chunk)
            self.chunks.extend(beginning_chunk)
        else:
            self.chunks = errs

        self.get_next_error(0, next=False)

    def get_next_error(self, i, reverse=False, next=True):
        self.forward = not self.forward if reverse else self.forward
        if self.forward and next:
            i += 1
        elif not self.forward and next:
            i -= 1

        if i > len(self.chunks) - 1:
            i = 0
        if i < 0:
            i = len(self.chunks) - 1
        # if self.chunks[i].a < self.chunks[self.i].a:
        #     self.reset_offset()
        self.i = i

        try:
            error = self.chunks[self.i]
        except IndexError as e:
            self.view.erase_regions('checkbounce_cycle_highlight')
            return

        self.error = error
        self.curr_word = self.view.substr(self.error)

        self.view.erase_regions("checkbounce_cycle_highlight")
        self.view.add_regions("checkbounce_cycle_highlight", [self.error], 'constant.language', 'dot')
        self.view.show_at_center(self.error)

        self.options = []
        self.corrs = []
        if self.forward:
            self.options.append(u"\u219D\tNext Error")
            self.options.append(u"\u219C\tPrevious Error")
        else:
            self.options.append(u"\u219C\tPrevious Error")
            self.options.append(u"\u219D\tNext Error")
        self.options.append(u"\u2766\tIgnore Word")
        self.options.append(u"\u2766\tAdd Word to Dictionary")
        all_corrs = self.checker.suggest(self.error)
        if all_corrs:
            for corr in all_corrs:
                self.corrs.append(corr)
                self.options.append(corr)
        else:
            self.corrs = None
            self.options.append(u"\u2767\tNo Suggestions")

        sublime.set_timeout(lambda: self.view.window().show_quick_panel(self.options, self.get_quick_panel), 0)

    def get_quick_panel(self, index):
        if index < 0:
            sublime.set_timeout(lambda: self.view.erase_regions('checkbounce_cycle_highlight'), 0)
        if index == 0:
            self.get_next_error(self.i)
        if index == 1:
            self.get_next_error(self.i, reverse=True)
        elif index == 2:
            self.checker.ignore_word(self.curr_word)
            for region in self.chunks:
                if self.view.substr(region) == self.curr_word:
                    self.chunks.remove(region)
            self.get_next_error(self.i)
        elif index == 3:
            self.checker.learn_word(self.curr_word)
            self.ignored.append(self.curr_word)
            for region in self.chunks:
                if self.view.substr(region) == self.curr_word:
                    self.chunks.remove(region)
            self.get_next_error(self.i)
        elif index > 3 and self.corrs:
            replacement = self.corrs[index - 4]
            self.view.run_command("check_bounce_replace", {"replacement": replacement, "a": self.error.a, "b": self.error.b})

            lr = len(replacement)
            lcw = len(self.curr_word)
            j = lr - lcw
            self.chunks.remove(self.error)
            self.parse_offset(j)
            self.get_next_error(self.i)
        elif index > 3 and not self.corrs:
            self.get_next_error(self.i)

    def parse_offset(self, j):
        replacement_chunks = []
        for k in range(len(self.chunks)):
            if k < self.i:
                replacement_chunks.append(self.chunks[k])
            elif k >= self.i:
                r = self.chunks[k]
                x = r.a + j
                y = r.b + j
                replacement_chunks.append(sublime.Region(x, y))
        self.reset += j
        self.chunks = replacement_chunks

    def reset_offset(self):
        old_chunks = []
        for k in range(len(self.chunks)):
            r = self.chunks[k]
            x = r.a - self.reset
            y = r.a - self.reset
            old_chunks.append(sublime.Region(x, y))
        self.reset = 0
        self.chunks = old_chunks
