# perl.py - sublimelint package for checking perl files

import subprocess
import sublime

from module_utils import get_executable, get_startupinfo

# start sublimelint perl plugin
import re
__all__ = ['run', 'language']
language = 'Perl'
linter_executable = 'perl'
description =\
'''* view.run_command("lint", "Perl")
        Turns background linter off and runs the default Perl linter
        (perl - c, assumed to be on $PATH) on current view.
'''


def is_enabled():
    global linter_executable
    linter_executable = get_executable('perl', 'perl')

    try:
        subprocess.Popen((linter_executable, '-v'), startupinfo=get_startupinfo(),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    except OSError:
        return (False, '"{0}" cannot be found'.format(linter_executable))

    return (True, 'using "{0}" for executable'.format(linter_executable))


def check(codeString):
    global linter_executable
    process = subprocess.Popen((linter_executable, '-c'),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                startupinfo=get_startupinfo())
    result = process.communicate(codeString)[0]

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

    def underlineRange(lineno, position, length=1):
        line = view.full_line(view.text_point(lineno, 0))
        position += line.begin()

        for i in xrange(length):
            underline.append(sublime.Region(position + i))

    def underlineRegex(lineno, regex, wordmatch=None, linematch=None):
        lines.add(lineno)
        offset = 0

        line = view.full_line(view.text_point(lineno, 0))
        lineText = view.substr(line)
        if linematch:
            match = re.match(linematch, lineText)
            if match:
                lineText = match.group('match')
                offset = match.start('match')
            else:
                return

        iters = re.finditer(regex, lineText)
        results = [(result.start('underline'), result.end('underline')) for result in iters if
                                            not wordmatch or result.group('underline') == wordmatch]

        for start, end in results:
            underlineRange(lineno, start + offset, end - start)

    for line in errors.splitlines():
        match = re.match(r'(?P<error>.+?) at .+? line (?P<line>\d+)(, near "(?P<near>.+?)")?', line)

        if match:
            error, line = match.group('error'), match.group('line')
            lineno = int(line) - 1

            near = match.group('near')
            if near:
                error = '{0}, near "{1}"'.format(error, near)
                underlineRegex(lineno, '(?P<underline>{0})'.format(re.escape(near)))

            lines.add(lineno)
            addMessage(lineno, error)

    return lines, underline, [], [], errorMessages, {}, {}
