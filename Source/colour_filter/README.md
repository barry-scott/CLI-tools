# colour_filter module and colour-filter command - colour parts of lines

## colour-filter command

The `colour-filter` command reads lines from its input,
colours parts of the line and prints the result on its output.

For example colour the output of a build script. Colour `Info:` in green
and all of the line that starts `Error:` in red.

``` bash
   $ ./build.sh 2>&1 | colour-filter '^Info:' green 'Error:.*' red
```

## colour_filter module

`ColourFilter` class

- `__init__()`

    Create instance of ColourFilter.

- `enableDebug( enable=True )`

    Turn on the debug output to help understand why patterns are not matching as expected.

- `define( pattern, colour )`

    When the regular express `pattern` is found in a line of input colour it as `colour` on the output.

    `colour` is either the string name of a list colour name seperated by ':' or ';'.
    E.g. `'red'` or 'red;bg-white'

    The builtin foreground colour names are:

        bold, black, brown, green, yellow, blue,
        magenta, cyan, gray, red, lightred, lightgreen,
        lightyellow, lightblue, lightmagenta, lightcyan
        ans white.

    The builtin background colour names are:

        bg-black, bg-brown, bg-green, bg-yellow,
        bg-blue, bg-magenta, bg-cyan, bg-gray
        and bg-white.

- `filterLines( input_file, output_file, line_buffered )`

    Read lines from `input_file` until end-of-file.
    Replace all matching patterns with their defined colour.
    Write each converted line to `output_file` and if `line_buffered` is `True`
    call `flush()` on the `output_file`.

### Example that colours lines of `build.log`

``` python
    from colour_filter import ColourFilter

    f = ColourFilter()
    f.define( 'Info:', 'green' )
    f.define( 'Error:', 'red;bg-white' )

    with open( 'build.log' ) as input_file:
        f.filterLines( input_file, sys.stdout, line_buffered=False )

```
