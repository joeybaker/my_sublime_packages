SublimeLinter
=============

A code-validating plugin with inline highlighting for the [Sublime Text 2](http://sublimetext.com "Sublime Text 2") editor.

Supports the following languages:

* Python - native, moderately-complete lint
* PHP - syntax checking via "php -l"
* Perl - syntax+deprecation checking via "perl -c"
* Ruby - syntax checking via "ruby -wc"
* Javascript - lint via node.js (you must install it, see http://nodejs.com) and built in jshint
* Objective-J - lint via built-in capp_lint (https://github.com/aparajita/capp_lint)

Installing
-----

*With the Package Control plugin:* The easiest way to install SublimeLinter is through Package Control, which can be found here:

    http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart ST2 and bring up the Command Palette (ctrl+shift+p [Windows, Linux] or cmd+shift+p [OS X]). Select "Package Control: Install Package", then select SublimeLinter. The advantage of using this method is that Package Control will automatically keep SublimeLinter up to date with the latest version.

*Without Git:* Download the latest source from http://github.com/Kronuz/SublimeLinter and copy the SublimeLinter folder to your Sublime Text "Packages" directory.

*With Git:* Clone the repository in your Sublime Text "Packages" directory:

> git clone git://github.com/Kronuz/SublimeLinter.git


The "Packages" directory is located at:

* Windows:
    %APPDATA%/Sublime Text 2/Packages/
* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/
* Linux:
    ~/.Sublime Text 2/Packages/

Using
-----
To enable the plugin to work by default, go to the Preferences menu and select "File Settings - User". Then add the following line to the array of prefs:
    "sublimelinter": true,

Don't include the trailing comma if it is the last item in the prefs array.

For detailed, up to date instructions on how to use and configure SublimeLinter, enter the following at the console

    view.run_command("lint")
or
    view.run_command("lint", "help")

You can turn on/off the linter via the command view.run_command("linter_on") (or "linter_off") -- even if you have not set a user preference before.

Note that the linter normally works in a background thread and is constantly refreshing when enabled.

3. To run a linter "once" (i.e. not always on in the background), you use
view.run_command("run_linter"), "LINTER") where "LINTER" is one of "Python", "PHP" or "pylint".
4. If you run a linter via a commmand as in 3. above, the realtime linter is automatically disabled. To reset to its previous state (on or off) AND to clear all visible "errors", you use the command
view.run_command("reset_linter").

Disabling Languages
-------------------

If you want to disable linting for specific languages, add their names (as listed above) to the file settings array "sublimelinter_disable".
For example, to disable Perl linting:

    "sublimelinter_disable":
        [
            "Perl"
        ],

The language name is case-insensitive.

Python and PEP8
---------------

If you use SublimeLinter for pep8 checks, you can ignore some of the conventions,
with the user preference "pep8_ignore".

Here is an example:

    "pep8_ignore":
        [
            "E501"
        ],

This configuration will ignore the long lines convention. You can see the list
of codes (as "E501") in [this file](https://github.com/jcrocholl/pep8/blob/master/pep8.py).

Python and PyFlakes
-------------------

If you use SublimeLinter for pyflakes checks, you can ignore some of the "undefined name xxx" errors (comes in handy if you work with post-processors, globals/builtins available only at runtime, etc.). You can control what names will be ignored with the user preference "pyflakes_ignore".

Example:

    "pyflakes_ignore":
        [
            "some_custom_builtin_o_mine",
            "A_GLOBAL_CONSTANT"
        ],
