# colour_text

# colour_text and colour-print command

`colour-print` is a command that makes printing coloured text
easier to do on Unix, macOS and Windows. It uses the `ColourText`
class to colour the text.

The command uses markup using `~colour-name text~`.

``` bash
    $ colour-print "~info Info:~ this is an ~em informational~ message"
    $ colour-print "~error Error: This is an error message"
```

The first argument is treated as a format string if there are more arguments.

``` bash
    $ colour-print "~info Info:~ Home folder is %s" "$HOME"
```

# class ColourText

The `ColourText` class converts strings with colour markup into
a form suitable for printing on a terminal that support colour
text. This include most terminal emulators on macOS, Windows
and Unix.

To colour a section of text use the marker followed by the colour
name a space and the text to be coloured ending with the marker.

``` python
    from colour_text import ColourText

    ct = ColourText()
    ct.initTerminal()

    print( ct.convert( "The next section is in green: ~green example~." ) )
```

To include the marker as literal text use two adjacent markers.

``` python
    from colour_text import ColourText

    ct = ColourText()
    ct.initTerminal()

    print( ct("A ~red literal tilda~ ~~ in the string") )
```

ColoutText can be use with gettext for internationalized applications.

``` python

    from colour_text import ColourText

    ct = ColourText()
    ct.initTerminal()

    message = "~red Error: cannot open file %s~"
    i18n_message = _(message)
    coloured_i18n_message = ct(i18n_message)
    formatted_message = coloured_i18n_message % (file_name,)

    print( formatted_message )

    # or in one line
    print ct( _("~red Error: cannot open file %s~") ) % (file_name,) )
```

class ColourText

- `__init__( marker='~' )`

    The `marker` is the string used to markup the colour sections
    which defaults to tilda (`~`).

- `initTerminal()`

    Ensure the terminal can display coloured text.

    Must be called on Windows and can be safely called on macOS and Unix systems.

- `define( name, colour_def )`

    Define a colour `name` for use in the marked up sections.
    The `colour_def` is a list of existing colour names
    or a single name.

    The builtin foreground colour names are:

        bold, black, brown, green, yellow, blue,
        magenta, cyan, gray, red, lightred, lightgreen,
        lightyellow, lightblue, lightmagenta, lightcyan
        and white.

    The builtin background colour names are:

        bg-black, bg-brown, bg-green, bg-yellow,
        bg-blue, bg-magenta, bg-cyan, bg-gray
        and bg-white.

    For example add the name `info` as green text and `error` as
    to be red text on a white background:

``` python
        ct = ColourText()
        ct.define( 'info', 'green' )
        ct.define( 'error', ('red', 'bg-white') )

        ct( "Error messages are ~error shown like this~" ) 
```

- `convert( colour_text )`

    Interpret the colour markup in the colour_text string
    and return a string suitable for printing on the terminal.

- `__call__( colour_text )`

    Call `convert( colour_text )` in a concise way.
