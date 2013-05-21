Focus Last Tab for Sublime Text
===============================

Always focus the last tab with ⌘+9 (on OS X) or Ctrl+9 (on Windows and Linux)
in Sublime Text 2 or 3, just like in your favorite browser!

Installation
------------

Install via [Package Control][1] to automatically keep up to date with new
versions.

To install manually, clone this repository into your `Packages` folder (e.g.
Sublime Text 3 on OS X):

```sh
cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages
git clone git://github.com/eproxus/focus_last_tab.git "Focus Last Tab"
```

Customize
---------

To customize, add your desired key binding to
_Preferences -> Key Bindings - User_:

```json
[
    { "keys": ["ctrl+end"], "command": "last_view" }
]
```

To keep the default key binding, add the following to
_Preferences -> Settings - User_:

```json
{
    "focus_last_tab_override": false
}
```

[1]: http://wbond.net/sublime_packages/package_control "Package Control"