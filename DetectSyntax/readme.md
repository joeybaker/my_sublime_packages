DetectSyntax
============

Support
-------

If you find DetectSyntax helpful, please consider making a donation.

<a href='http://www.pledgie.com/campaigns/16864'><img alt='Click here to lend your support to: DetectSyntax and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/16864.png?skin_name=chrome' border='0' /></a>

Description
-----------

DetectSyntax is a plugin for Sublime Text 2 that allows you to detect the syntax of files that might not otherwise be detected properly. For example, files with the `.rb` extension are usually Ruby files, but when they are found in a Rails project, they could be RSpec spec files, Cucumber step files, Ruby on Rails files (controllers, models, etc), or just plain Ruby files. This is actually the problem I was trying to solve when I started working on this plugin.

Installation
------------

DetectSyntax can be installed in a variety of ways:

* Through Package Control [http://wbond.net/sublime_packages/package_control] (http://wbond.net/sublime_packages/package_control)

	Open Package Control  
	Select 'Install Package'  
	Find and select 'DetectSyntax'

* By cloning this repository in Packages

		cd into your Packages folder  
		git clone git://github.com/phillipkoebbe/DetectSyntax.git .

* By downloading the files and placing them in a directory under Packages, such as DetectSyntax or User

	If you don't put the files in Packages/User (you *can*, but probably shouldn't), make sure they live in Packages/DetectSyntax. If you download and extract a compressed archive from GitHub, the directory will be `phillipkoebbe-DetectSyntax`. Remove `phillipkoebbe-`.

Usage
-----

DetectSyntax is based on the idea that there are rules for selecting a certain syntax. You define the rules, the plugin checks them. The first one to pass wins. If you have need of multiple conditions that must be met, you should use the function rule. See the default settings file for more on function rules.

Create your own rules in `Packages/User/DetectSyntax.sublime-settings`. The easiest way to get started is to just copy the default settings file found in `Packages/DetectSyntax/DetectSyntax.sublime-settings` to your user directory and modify it to meet your needs. Make sure you rename the `default_syntaxes` key to just `syntaxes`. If you don't, you will overwrite the default syntaxes and they will not work.

See the default settings file for examples and comments related to creating rules.

Credits
-------

It all started by forking the plugin created by JeanMertz (1). I modified it quite extensively until I ended up with something entirely my own (2). @maxim and @omarramos commented on the gist and suggested it should be part of Package Control. As I had created it solely for my own consumption, it seemed a bit "hard-coded" to be valuable as a package, but then I took a look at SetSyntax (3) and saw how using settings would make it very flexible. That set me on the path that led to DetectSyntax.

(1) [https://gist.github.com/925008] (https://gist.github.com/925008)  
(2) [https://gist.github.com/1497794] (https://gist.github.com/1497794)  
(3) [https://github.com/aparajita/SetSyntax] (https://github.com/aparajita/SetSyntax)

Contributing
------------

* Fork the project.
* Use topic branch.
* Make pull request.

History
-------
2012-11-18

* Added support for zsh config files. [Thanks Benjamin Smith]

2012-10-25

* Added ability to match all rules. [Thanks for the idea Kirk Strauser]

2012-10-20

* Added jbuilder to the Ruby rule. [Thanks Aaron Crespo]
* Expanded Vagrantfile rule to catch extensions (like Vagrantfile.local).

2012-09-01

* Removed Puppet files from Ruby syntax. See https://github.com/phillipkoebbe/DetectSyntax/issues/11 for details.
* Added some more files to YAML, PHP, XML, INI, and ShellScript. [Thanks Chris Jones]

2012-08-13

* User-defined syntax rules get processed first now. [Closes #11]

2012-08-07

* Added rule to Ruby syntax for Puppet (pp) files.

2012-07-12

* Added support for .simplecov (https://github.com/colszowka/simplecov#using-simplecov-for-centralized-config) [Closes #9, thanks Andrey Botalov]
* Added Preferences menu [Closes #8, thanks Kirk Strauser]
* Create a bare-bones user settings file if one doesn't exist

2012-07-02

* Fixed improper handling of directories with non-ascii characters [Closes #5, thanks Andrew Dryga]

2012-06-28

* Better handling of file defining a function potentially not existing.

2012-06-26

* Added new_file_syntax so new files can have a syntax applied immediately.

2012-06-20

* Added rule for *.thor (thanks Magnus Rex).

2012-04-13

* Renamed the `syntaxes` key to `default_syntaxes` so it is no longer necessary to duplicate default rules in User/DetectSyntax.sublime-settings.

2012-03-23

* Added rule type of 'binary' which builds a shebang regexp for the user.

2012-03-22

* Check to make sure the syntax file exists before trying to set it. [Closes #3, thanks tito]
