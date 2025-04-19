import sys
import update_linux

def main():
    try:
        sys.exit( update_linux.UpdateFedora().main( sys.argv ) )

    except KeyboardInterrupt:
        print()
        print( "Error: exiting at user's requrest (SIGINT)" )
        sys.exit( 1 )

if __name__ == '__main__':
    main()
