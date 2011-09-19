SublimeLinter
=============

SublimeLinter is a plugin that supports "lint" programs (known as "linters"). SublimeLinter highlights
lines of code the linter deems to contain (potential) errors. It also
supports highlighting special annotations (for example: TODO) so that they
can be quickly located.

SublimeLinter has built in linters for the following languages:

* Javascript - lint via built in [jshint](http://jshint.org) run by JavaScriptCore on OS X or node.js on other platforms. You must install node.js, see [the node.js site](http://nodejs.com) for instructions.
* Objective-J - lint via built-in [capp_lint](https://github.com/aparajita/capp_lint)
* Perl - syntax+deprecation checking via "perl -c"
* PHP - syntax checking via "php -l"
* Python - native, moderately-complete lint
* Ruby - syntax checking via "ruby -wc"

Installing
----------
**With the Package Control plugin:** The easiest way to install SublimeLinter is through Package Control, which can be found at this site: [http://wbond.net/sublime\_packages/package\_control](http://wbond.net/sublime\_packages/package\_control)

Once you install Package Control, restart ST2 and bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select SublimeLinter when the list appears. The advantage of using this method is that Package Control will automatically keep SublimeLinter up to date with the latest version.

**Without Git:** Download the latest source from [github](http://github.com/Kronuz/SublimeLinter) and copy the SublimeLinter folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory:

    git clone git://github.com/Kronuz/SublimeLinter.git

The "Packages" directory is located at:

* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/
* Linux:
    ~/.Sublime Text 2/Packages/
* Windows:
    %APPDATA%/Sublime Text 2/Packages/

Using
-----
The best way to use SublimeLinter is as a background linter, which is the default behavior. Every time the text changes, a lint run is queued for execution. If you find that background linting slows down the UI too much, you can unset this user preference (or set it to false) and use the Control+Command+l (OS X) or Control+Alt+l (Linux/Windows) key equivalent or the Command Palette to run it only on demand.

To disable background linting, go to the Preferences menu and select "File Settings - User". Then add the following line to the settings:

    "sublimelinter": false,

Don't include the trailing comma if it is the last item in the prefs array.

Within a file whose language/syntax is supported by SublimeLinter, you control SublimeLinter via the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows). The available commands are:

* SublimeLinter: Lint Current File — Lints the current file, highlights any errors and displays how many errors were found.
* SublimeLinter: Enable Background Linting — Enables the background linter for the current view and lints it.
* SublimeLinter: Disable Background Linting — Disables the background linter for the current view and clears all lint errors.
* SublimeLinter: Reset — Clears all lint errors and enables background linting if it has not explicitly been disabled.
* SublimeLinter: Show Commands — Shows commands available for use by other plugins or via the console.

Depending on the file and the current state of background enabling, some of the commands will not be available.

When an error is highlighted by the linter, putting the cursor on the offending line will result in the error message being displayed on the status bar.

You can quickly move to the next/previous lint error with the following key equivalents:

**OS X**
next: Control+Command+e
prev: Control+Command+Shift+e

**Linux, Windows**
next: Control+Alt+e
prev: Control+Alt+Shift+e

By default the search will wrap. You can turn wrapping off with the user setting:

    "sublimelinter_wrap_find": false

Configuring
-----------
There are a number of configuration options available to customize the behavior of SublimeLinter and its linters. For the latest information on what options are available, select the menu item Preferences->Package Settings->SublimeLinter->Settings - Default.

### Customizing colors
There are three types of "errors" flagged by sublime lint: illegal,
violation, and warning. For each type, SublimeLinter will indicate the offending
line and the character position at which the error occurred on the line.

By default SublimeLinter will outline offending lines using the background color
of the "sublimelinter.<type>" theme style, and underline the character position
using the background color of the "invalid.<type>" theme style, where <type>
is one of the three error types.

If these styles are not defined, the color will be black when there is a light
background color and black when there is a dark background color. You may
define a single "sublimelinter" or "invalid" style to color all three types,
or define separate substyles for one or more types to color them differently.
Most themes have an "invalid" theme style defined by default.

If you want to make the offending lines glaringly obvious (perhaps for those
who tend to ignore lint errors), you can set the user setting:

    "sublimelinter_fill_outlines": true

When this is set true, lines that have errors will be colored with the background
and foreground color of the "sublime.<type>" theme style. Unless you have defined
those styles, this setting should be left false.

You may also mark lines with errors by putting an "x" in the gutter with the user setting:

    "sublimelinter_gutter_marks": true

To customize the colors used for highlighting errors and user notes, add the following
to your theme (adapting the color to your liking):

    <dict>
        <key>name</key>
        <string>SublimeLinter Annotations</string>
        <key>scope</key>
        <string>sublimelinter.notes</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FFFFAA</string>
            <key>foreground</key>
            <string>#FFFFFF</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Outline</string>
        <key>scope</key>
        <string>sublimelinter.illegal</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FF4A52</string>
            <key>foreground</key>
            <string>#FFFFFF</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Underline</string>
        <key>scope</key>
        <string>invalid.illegal</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FF0000</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Warning Outline</string>
        <key>scope</key>
        <string>sublimelinter.warning</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#DF9400</string>
            <key>foreground</key>
            <string>#FFFFFF</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Warning Underline</string>
        <key>scope</key>
        <string>invalid.warning</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FF0000</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Violation Outline</string>
        <key>scope</key>
        <string>sublimelinter.violation</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#ffffff33</string>
            <key>foreground</key>
            <string>#FFFFFF</string>
        </dict>
    </dict>
    <dict>
        <key>name</key>
        <string>SublimeLinter Violation Underline</string>
        <key>scope</key>
        <string>invalid.violation</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>#FF0000</string>
        </dict>
    </dict>

Troubleshooting
---------------
If a linter does not seem to be working, you can check the ST2 console to see if it was enabled. When SublimeLinter is loaded, you will see messages in the console like this:

    Reloading plugin /Users/aparajita/Library/Application Support/Sublime Text 2/Packages/SublimeLinter/sublimelinter_plugin.py
    SublimeLinter: JavaScript enabled (using JavaScriptCore)
    SublimeLinter: annotations enabled (built in)
    SublimeLinter: Objective-J enabled (built in)
    SublimeLinter: Perl enabled (using "perl" for executable)
    SublimeLinter: PHP enabled (using "php" for executable)
    SublimeLinter: Python enabled (built in)
    SublimeLinter: Ruby enabled (using "ruby" for executable)
    SublimeLinter: pylint disabled (the pylint module could not be imported)

Let's say the PHP linter is not working. If you look at the console, you may see a message like this:

    SublimeLinter: PHP disabled ("php" cannot be found)

This means that the php executable cannot be found on your system, which means it is not installed or not in your executable path.
