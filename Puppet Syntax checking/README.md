# Puppet Syntax Checker for Modules
## Checks Puppet modules for syntax errors when you save a module.

### Usage

Automatically executes the Puppet syntax check on any puppet modules that you save.

### Settings

```json
{
    // Plugin settings

    // Turn the debug output on/off
    "show_debug": true,

    // Use an alternative path for the puppet executable
    "puppet_path": "/usr/bin/puppet", 

    // These setting control when & if any errors detected are shown.
    "puppetsyntax_show_gutter_marks": true,
    "puppetsyntax_outline_for_errors": true,
    "puppetsyntax_show_errors_on_save": true,
    "puppetsyntax_show_quick_panel": false,

    // Pass any extra optional parameters to Puppet.
    "puppetsyntax_additional_args": []
}
```