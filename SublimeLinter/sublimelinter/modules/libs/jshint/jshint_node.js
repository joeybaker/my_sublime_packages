/*jshint node:true */

/*
    Created by Aparajita Fishman  (https://github.com/aparajita)

    This code is adapted from the node.js jshint module to work with stdin instead of a file.

    ** Licensed Under **

    The MIT License
    http://www.opensource.org/licenses/mit-license.php

    usage: node /path/to/jshint_wrapper.js
*/

var _fs = require('fs'),
    _sys = require('sys'),
    _path = require('path'),
    _jshint = require(_path.join(_path.dirname(process.argv[1]), 'jshint.js')),
    _config;

function _removeJsComments(str) {
    str = str || '';
    str = str.replace(/\/\*[\s\S]*(?:\*\/)/g, ''); //everything between "/* */"
    str = str.replace(/\/\/[^\n\r]*/g, ''); //everything after "//"
    return str;
}

function _loadAndParseConfig(filePath) {
    var config = {},
        fileContent;
    try {
        if (_path.existsSync(filePath)) {
            fileContent = _fs.readFileSync(filePath, "utf-8");
            config = JSON.parse(_removeJsComments(fileContent));
        }
    } catch (e) {
        _sys.puts("Error opening config file " + filePath + '\n');
        _sys.puts(e + "\n");
        process.exit(1);
    }
    return config;
}

function _mergeConfigs(homerc, cwdrc) {
    var homeConfig = _loadAndParseConfig(homerc),
        cwdConfig = _loadAndParseConfig(cwdrc),
        prop;

    for (prop in cwdConfig) {
        if (typeof prop === 'string') {
            if (prop === 'predef') {
                homeConfig.predef = (homeConfig.predef || []).concat(cwdConfig.predef);
            } else {
                homeConfig[prop] = cwdConfig[prop];
            }
        }
    }
    return homeConfig;
}

function hint() {
    var defaultConfig = _path.join(process.env.HOME, '.jshintrc'),
        projectConfig = _path.join(process.cwd(), '.jshintrc'),
        config = _mergeConfigs(defaultConfig, projectConfig),
        code = '';

    process.stdin.resume();
    process.stdin.setEncoding('utf8');

    process.stdin.on('data', function (chunk) {
        code += chunk;
    });

    process.stdin.on('end', function () {
        var results = [];

        if (!_jshint.JSHINT(code, config)) {
            _jshint.JSHINT.errors.forEach(function (error) {
                if (error) {
                    results.push(error);
                }
            });
        }

        _sys.puts(JSON.stringify(results));
        process.exit(0);
    });
}

hint();
