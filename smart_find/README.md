# smart-find

smart-find makes it easier to access the advanced features of
find and grep.

## Usage

Use the `-help` option to show the smart-find usage.

```bash
    $ smart-find -help
    Usage: smart-find

        -help               - print this help
        -contains (-c)      - grep for string in found files
        -ignore-case (-i)   - ignore case when greping
        -iname (-in)        - ignore case of filenames
        -save-config        - write the default config
                              into /Users/barry/Library/Preferences/smart-find.json
        -debug              - print the find command line
        -<int>              - limit find to a max depth of <int>
```

## configuration

smart-find follows the conventions of macOS and Linux XDG to look for configuration files.

You can see the default configuration file path in the `smart-find -help` output

* macos - `~/Library/Preferences/smart-find.json`
* linux - `~/.config/smart-find.json`

Use the `smart-find -save-config` to create a config file with the default
configuration options:

The default configuration is:

```json
    {
        "folders_to_prune": [".svn", ".git", ".hg"],
        "files_to_prune":   ["*~"]
    }
```

The following items are supported:

* folders_to_prune is a list of folders that will be ignored
* files_to_prune is a list of file patterns that will be ignored

