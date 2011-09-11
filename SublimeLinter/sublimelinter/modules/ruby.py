# ruby.py - sublimelint package for checking ruby files

import subprocess

from module_utils import get_startupinfo


def is_enabled():
    try:
        subprocess.Popen(('ruby', '-v'), startupinfo=get_startupinfo())
    except OSError:
        return (False, 'ruby cannot be found')

    return True


def check(codeString, filename):
    process = subprocess.Popen(('ruby', '-wc'),
                  stdin=subprocess.PIPE,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  startupinfo=get_startupinfo())
    result = process.communicate(codeString)[0]

    return result

# start sublimelint Ruby plugin
import re
__all__ = ['run', 'language']
language = 'Ruby'
description =\
'''* view.run_command("lint", "Ruby")
        Turns background linter off and runs the default Ruby linter
        (ruby -c, assumed to be on $PATH) on current view.
'''


def run(code, view, filename='untitled'):
    errors = check(code, filename)

    lines = set()
    underline = []  # leave this here for compatibility with original plugin

    errorMessages = {}

    def addMessage(lineno, message):
        message = str(message)
        if lineno in errorMessages:
            errorMessages[lineno].append(message)
        else:
            errorMessages[lineno] = [message]

    for line in errors.splitlines():
        match = re.match(r'^.+:(?P<line>\d+):\s+(?P<error>.+)', line)

        if match:
            error, line = match.group('error'), match.group('line')

            lineno = int(line) - 1
            lines.add(lineno)
            addMessage(lineno, error)

    return lines, underline, [], [], errorMessages, {}, {}
