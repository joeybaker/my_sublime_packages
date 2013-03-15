# Description

Clipboard functionality to copy a block of text from PDF and paste it with the new lines and hyphenated words stripped so that it is a clean paste of a block of text into the target area. 

Given that we do a lot of work between PDFs and Markdown in drafting of documents, it seemed necessary to work on the paste functionality a bit. 

# Installation

## Install using Sublime Package Control

If you are using Will Bond's excellent Sublime Package Control, you can easily install Paste PDF via the Package Control: Install Package menu item. The Paste PDF package is listed there. See [Package Control](http://wbond.net/sublime_packages/package_control)

## Install using Git

You can install the theme and keep up to date by cloning the repo directly into your Packages directory in the Sublime Text 2 application settings area. You can locate your Sublime Text 2 Packages directory by using the menu item Preferences -> Browse Packages. While inside the Packages directory, clone the theme repository using the command below:

```
$ git clone https://github.com/compleatang/sublimetext-pastepdf
```

## Manual Install

To download and install package manually:

* Download the files using the GitHub .zip download option
* Unzip the files and rename the folder to Paste PDF
* Move the folder to your Sublime Text 2 Packages directory

# Using

## Base Paste PDF Text Block

The default keybinding is CTRL+ALT+V in Linux and Windows, CTRL+Super+V on OsX. To assign a new keybinding:

* Open ".../Packages/User/Default.sublime-keymap"
* The relevant command name is "paste_pdf"

```
  { "keys": ["ctrl+alt+v"], "command": "paste_pdf" }
```

The function will also correct French accents thanks to the kind help of Gery Casiez. 

## Paste PDF Text Block with Pandoc Footnote

One thing I often do is paste a text block but then need to mark it for citation. There is a new command that will take care of that for you, called `paste_pdf_pandoc`. This command will preformat the text block using the clean_paste function, wrap the entire block in double quotes, add Pandoc's `^[]` footnote formatting, and place the cursor so you can instantly put in the BibTex reference or citation holder. The default keybinding for this is CTRL+ALT+SHIFT+V in Linux & Windows, and CTRL+SHIFT+Super+v in OsX.

# [Source Code](https://github.com/compleatang/sublimetext-pastepdf)

MIT License - (c) 2012 - Watershed Legal Services, PLLC

# TODO

[ ] Build option to turn on or off block quoting of pandoc paste. For now default is to put the paste in a block quote.
