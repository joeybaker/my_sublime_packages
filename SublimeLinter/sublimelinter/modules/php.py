# php.py - sublimelint package for checking php files

import subprocess

from module_utils import get_executable, get_startupinfo


# start sublimelint php plugin
import re
__all__ = ['run', 'language']
language = 'PHP'
linter_executable = 'php'
description =\
'''* view.run_command("lint", "PHP")
        Turns background linter off and runs the default PHP linter
        (php - l, assumed to be on $PATH) on current view.
'''


def is_enabled():
    global linter_executable
    linter_executable = get_executable('php', 'php')

    try:
        subprocess.Popen((linter_executable, '-v'), startupinfo=get_startupinfo(),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    except OSError:
        return (False, '"{0}" cannot be found'.format(linter_executable))

    return (True, 'using "{0}" for executable'.format(linter_executable))


def check(codeString):
    global linter_executable
    process = subprocess.Popen((linter_executable, '-l', '-d display_errors=On'),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                startupinfo=get_startupinfo())

    try:
        result = process.communicate(codeString)[0]
    except:
        result = ''

    return result


def run(code, view, filename='untitled'):
    errors = check(code)

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
        match = re.match(r'^Parse error:\s*syntax error,\s*(?P<error>.+?)\s+in\s+.+?\s*line\s+(?P<line>\d+)', line)

        if match:
            error, line = match.group('error'), match.group('line')

            lineno = int(line) - 1
            lines.add(lineno)
            addMessage(lineno, error)

    return lines, underline, [], [], errorMessages, {}, {}
