import sublime
if int(sublime.version()) >= 3000:
    from queue import Queue, Empty
else:
    from Queue import Queue, Empty
import threading
import time


class Daemon:
    running = False
    callback = None
    q = Queue()
    last_run = {}

    def start(self, callback):
        self.callback = callback

        if self.running:
            self.q.put('reload')
            return
        else:
            self.running = True
            threading.Thread(target=self.loop).start()

    def reenter(self, view_id):
        self.callback(view_id)

    def loop(self):
        views = {}

        while True:
            try:
                try:
                    item = self.q.get(True, 0.5)
                except Empty:
                    for view_id, ts in views.copy().items():
                        if ts < time.time() - 0.5:
                            self.last_run[view_id] = time.time()
                            del views[view_id]
                            self.reenter(view_id)

                    continue

                if isinstance(item, tuple):
                    view_id, ts = item
                    if view_id in self.last_run and ts < self.last_run[view_id]:
                        continue

                    views[view_id] = ts

                elif isinstance(item, (int, float)):
                    time.sleep(item)

                elif isinstance(item, str):
                    if item == 'reload':
                        pass

                else:
                    pass
            except Exception as e:
                pass

    def hit(self, view):
        self.q.put((view.id(), time.time()))

    def delay(self):
        self.q.put(0.01)


if not 'spelling' in globals():
    spell_queue = Daemon()

    spell_errors = {}
    spell_error_regions = {}
    words = {}
    spell_checkers = {}
    spelling = True

if not 'grammar' in globals():
    grammar_queue = Daemon()

    grammar_errors = {}
    grammar_error_regions = {}
    grammar_checkers = {}
    grammar = True
