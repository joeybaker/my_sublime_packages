Joey's Sublime Text 3 Packages
===================

Uses the new, fancy way of doing things with package control and "package files" wherever possible. Where not possible, packages are manually installed and switched to their Sublime Text 3 branch via `git subtree`.

## `add.sh`
Simple bash script that makes adding a package manually easy.

### Usage
```shell
sh add.sh NameOfPackageInstallFolder http://github.com/package/repo/url.git nameOfST3branch
```

Takes 3 arguments
1. name of the package install folder. Usually, this is specified in the package manual install instructions.
2. the git url to get the package.
3. the name of the branch in the repo that has the st3 version of the package.

## Install

2. close sublime text
3. past the following code into your shell

    ```bash
    cd ~/Library/Application\ Support/Sublime\ Text\ 3/ && rm -rf Packages Installed\ Packages; git clone -b st3 https://joeybaker@github.com/joeybaker/my_sublime_packages.git && mv my_sublime_packages/Packages Packages && mv my_sublime_packages/* . && rm -rf my_sublime_packages
    ```

3. [install package control](https://sublime.wbond.net/installation)
4. Install packages for the linter `sudo npm i -g csslint jshint`


## Upgrading to ST3

If you're not going to use my setup, that's cool, here's how to upgrade yourself.

1. I highly recommend installing the [caniswitchtosublimetext3](http://www.caniswitchtosublimetext3.com/) plugin in sublime text 2.
2. manually copy over the `Color Scheme - User` & `User` folders from the sublime text 2 library to the sublime text 3 library `Packages` folder.
3. Install [Package Control](https://sublime.wbond.net/installation)
4. Use package control to install the packages that are compatible with Sublime Text 3.
5. Use `add.sh` install the packages that aren't compatible.
