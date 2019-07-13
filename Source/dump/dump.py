#!/usr/bin/python3
import sys

batch_size = 16

def main( argv ):
    offset = 0
    limit = 2**32

    if len(argv) <= 1:
        print( 'Usage: dump <filename> [<limit>]' )
        return 1

    f = open( argv[1], 'rb' )

    if len(argv) > 2:
        limit = int( argv[2], 16 )

    while offset < limit:
        all_parts = []
        buf = f.read( batch_size )
        if len(buf) == 0:
            break

        if len( buf ) < batch_size:
            buf = buf + (b'\x00' * batch_size)

        for i in range( batch_size-1, -1, -1 ):
            all_parts.append( '%2.2x' % (buf[i],) )

        all_parts.append( ' %8.8x ' % (offset,) )

        all_str = []
        for i in range( batch_size ):
            r = repr( buf[i:i+1] )
            if len(r) != 4:
                all_str.append( '.' )
            else:
                all_str.append( r[2] )

        all_parts.append( ''.join( all_str ) )

        print( '%s %s %s %s-%s %s %s %s-%s %s %s %s-%s %s %s %s  %s  %s' % tuple( all_parts ) )

        offset += batch_size

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
