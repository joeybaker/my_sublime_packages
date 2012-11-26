Sublime Text 2 - Revert All Files Plugin
===============================

Plugin for Sublime Text 2 adding a window command to revert all unsaved files to their last saved state.

## Description

Have you ever done a search-and-replace on an entire large project, only to then realize that you made an irreversable mistake? That happened to me recently and I was shocked to find that Sublime Text 2 did not have a Replace All Files command (at least not that I could find).

This plugin adds the command ('revert_all') and a handy menu item in the File menu. This command will first open a confirmation dialog making sure you REALLY want to revert and undo all unsaved changes (because it could be a big pain to restore them again)...

The command has not yet been given a keyboard shortcut, you can always add this in your User preferences if you want; if everyone seems to want this though I'll be happy to add it. Or if you're feeling froggy, jump on in by forking the repo and sending a pull request with your patch! :)

## Installation

The easiest and quickest way to install is with [Package Control](http://wbond.net/sublime\_packages/package\_control) (see the next sub-section).

To manually install Revert All Files follow these steps on your command line (e.g. Terminal):

 * cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages (substitute for the path to your Sublime Text 2 packages directory if you're not using OS X).
 * git clone git://github.com/allstruck/Sublime-Text-2-Revert-All-Files.git RevertAllFiles

### Package Control

 * Bring up the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select Revert All Files when the list appears.

Package Control will automatically keep Revert All Files up to date with the latest version if you use this method.