import sublime
import sublime_plugin

import time

from .lint import util
from .lint.const import STATUS_BUSY_KEY
from .lint import events


INITIAL_DELAY = 1
CYCLE_TIME = 200
TIMEOUT = 20


State = {
    'active_view': None,
    'running': {}
}


def plugin_loaded():
    State.update({
        'active_view': sublime.active_window().active_view()
    })


def plugin_unloaded():
    events.off(on_begin_linting)
    events.off(on_finished_linting)



@events.on(events.BEGIN_LINTING)
def on_begin_linting(vid):
    State['running'][vid] = time.time()

    active_view = State['active_view']
    if active_view and active_view.id() == vid:
        sublime.set_timeout_async(lambda: draw(**State), INITIAL_DELAY * 1000)


@events.on(events.FINISHED_LINTING)
def on_finished_linting(vid):
    State['running'].pop(vid, None)

    active_view = State['active_view']
    if active_view and active_view.id() == vid:
        draw(**State)


class UpdateState(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        active_view = util.get_focused_view(view)

        State.update({
            'active_view': active_view
        })

        draw(**State)



# indicators = [
#     'Linting .. ',
#     'Linting  ..',
#     'Linting . .',
# ]

# indicators = ['( .)', '(. )']
indicators = ['(\)', '(|)', '(/)', '(-)']


def draw(active_view, running, **kwargs):
    if not active_view:
        return

    vid = active_view.id()
    start_time = running.get(vid, None)
    now = time.time()
    if start_time and (INITIAL_DELAY <= (now - start_time) < TIMEOUT):
        num = len(indicators)
        text = indicators[int((now - start_time) * 1000 / CYCLE_TIME) % num]
        active_view.set_status(STATUS_BUSY_KEY, text)
        sublime.set_timeout_async(lambda: draw(**State), CYCLE_TIME)
    else:
        active_view.erase_status(STATUS_BUSY_KEY)
