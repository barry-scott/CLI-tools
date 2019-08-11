# smart-find

smart-find makes it easier to access the advanced features of
find and grep.

## Usage

Use the `-help` option to show the sfind usage.

    $ smart-find -help
    Usage: smart-find

        -help               - print this help
        -contains (-c)      - grep for string in found files
        -ignore-case (-i)   - ignore case when greping
        -iname (-in)        - ignore case of filenames
        -save-config        - write the default config
                              into /Users/barry/Library/Preferences/sfind.json
        -debug              - print the find command line
        -<int>              - limit find to a max depth of <int>

## configuration

sfind follows the conventions of macOS and Linux XDG to look for configuration files.
You can see the default configuration file path in the sfind -help output

 * macos - `~/Library/Preferences/sfind.json`
 * linux - `~/.config/sfind.json`

Use the `sfind -save-config` to create a config file with the default
configuration options:

The default configuration is:

    {
        "folders_to_prune": [".svn", ".git", ".hg"],
        "files_to_prune":   ["*~"]
    }

 * folders_to_prune is a list of folders that will be ignored
 * files_to_prune is a list of file patterns that will be ignored

