# [Floobits](https://floobits.com/) plugin for Sublime Text 2 & 3

Real-time collaborative editing. Think Etherpad, but with native editors. This is the plugin for Sublime Text. We also have plugins for [Emacs](https://github.com/Floobits/floobits-emacs), [Vim](https://github.com/Floobits/floobits-vim), and [IntelliJ](https://github.com/Floobits/floobits-intellij).

### Development status: Reasonably stable. We dogfood it daily and rarely run into issues.

# Installation instructions

* [Create a Floobits account](https://floobits.com/signup/) or [sign in with GitHub](https://floobits.com/login/github/?next=/dash/).
* If you have [Sublime Package Control](http://wbond.net/sublime_packages/package_control), go to Package Control → Install Package and search for Floobits. Select the Floobits package and install it.

* If you don't have Package Control (or you prefer to install the plugin manually), clone this repository or download and extract [this tarball](https://github.com/Floobits/floobits-sublime/archive/master.zip).
* Rename the directory to "Floobits".
* In Sublime Text, go to Preferences -> Browse Packages.
* Drag, copy, or move the Floobits directory into your Packages directory.

If you'd rather create a symlink instead of copy/moving, run something like:

    ln -s ~/code/floobits-sublime ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Floobits

# Configuration

All configuration settings are stored in `~/.floorc`. If you don’t have a `~/.floorc` file, the plugin will create one and open it in Sublime Text. It will also open a web page showing the minimal information you’ll need to put in your `~/.floorc`. After saving the file, restart Sublime Text.

# Using Floobits to Collaborate

After creating your account, you’ll want to create a workspace or two. A workspace is a collection of files and buffers that users can collaborate on.

See https://floobits.com/help/plugins/#sublime-usage for instructions on how to create workspaces and collaborate with others.


# Errata

## Windows
The Python included with the Windows version of Sublime Text 2 does not have the [select](http://docs.python.org/2/library/select.html) module. This means the plugin won't work with Sublime Text 2 on Windows. Windows users must install Sublime Text 3 if they want to use this plugin. Sorry, there's nothing we can do about this. `:(`


## Linux
On Linux, Sublime Text 2 and 3 ship with a broken SSL module. This is a known bug. We try to work around it by running an SSL proxy using the system Python.


## OS X
Our plugin doesn't work on 10.6 and earlier. This appears to be a bug in OS X. Please upgrade to a newer version.


# Help

If you have trouble setting up or using this plugin, please [contact us](https://floobits.com/help#support).
