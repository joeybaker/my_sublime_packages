# Note: Unlike what is the case for language linter modules,
# changes made to this module will NOT take effect until
# Sublime Text is restarted.
import glob
import os
import sys


class Loader(object):
    '''utility class to load (and reload if necessary) SublimeLinter modules'''
    def __init__(self, basedir, linters, descriptions):
        '''assign relevant variables and load all existing linter modules'''
        self.basedir = basedir
        self.basepath = 'sublimelinter/modules'
        self.linters = linters
        self.modpath = self.basepath.replace('/', '.')
        self.ignored = ('__init__', 'module_utils')
        self.descriptions = descriptions
        self.fix_path()
        self.load_all()

    def fix_path(self):
        if os.name != 'posix':
            return

        path = os.environ['PATH']

        if path:
            dirs = path.split(':')

            if '/usr/local/bin' not in dirs:
                dirs.insert(0, '/usr/local/bin')

            if '~/bin' not in dirs and '$HOME/bin' not in dirs:
                dirs.append('$HOME/bin')

            os.environ['PATH'] = ':'.join(dirs)

    def load_all(self):
        '''loads all existing linter modules'''
        for modf in glob.glob('{0}/*.py'.format(self.basepath)):
            base, name = os.path.split(modf)
            name = name.split('.', 1)[0]

            if name in self.ignored:
                continue

            self.load_module(name)

    def load_module(self, name):
        '''loads a single linter module'''
        fullmod = '{0}.{1}'.format(self.modpath, name)

        # make sure the path didn't change on us (this is needed for submodule reload)
        pushd = os.getcwd()
        os.chdir(self.basedir)

        __import__(fullmod)

        # this following line of code does two things:
        # first, we get the actual module from sys.modules,
        #    not the base mod returned by __import__
        # second, we get an updated version with reload()
        #    so module development is easier
        # (to make sublime text reload language submodule,
        #  just save sublimelinter_plugin.py )
        mod = sys.modules[fullmod] = reload(sys.modules[fullmod])

        # update module's __file__ to absolute path so we can reload it
        # if saved with sublime text
        mod.__file__ = os.path.abspath(mod.__file__).rstrip('co')

        is_enabled = True

        try:
            language = mod.language
            lc_language = language.lower()
            enabled = mod.is_enabled()

            if isinstance(enabled, bool):
                is_enabled = enabled
                reason = ''
            elif isinstance(enabled, tuple) and len(enabled) == 2:
                is_enabled = enabled[0]
                reason = enabled[1]
            else:
                is_enabled = False
                reason = 'Could not determine the enabled state'

            if is_enabled:
                print 'SublimeLinter: {0} enabled{1}'.format(language, ' ({0})'.format(reason) if reason else '')
                self.linters[lc_language] = mod
            else:
                print 'SublimeLinter: {0} disabled ({1})'.format(language, reason)

                if lc_language in self.linters:
                    del self.linters[lc_language]
        except AttributeError:
            print 'SublimeLinter: loaded {0} - no language specified'.format(name)
            is_enabled = False
        except:
            print 'SublimeLinter: general error importing {0} ({1})'.format(name, language)
            is_enabled = False

        if is_enabled:
            try:
                self.descriptions.append(mod.description)
            except AttributeError:
                print 'SublimeLinter: no description present for {0}'.format(language)
            except:
                print 'SublimeLinter: error seeking description of {0}'.format(language)

        os.chdir(pushd)

    def reload_module(self, module):
        '''reload a single linter module
           This method is meant to be used when editing a given
           linter module so that changes can be viewed immediately
           upon saving without having to restart Sublime Text'''
        fullmod = module.__name__
        if not fullmod.startswith(self.modpath):
            return

        name = fullmod.replace(self.modpath + '.', '', 1)
        self.load_module(name)
