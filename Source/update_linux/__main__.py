import sys
import update_linux

def main():
    sys.exit( update_linux.UpdateFedora().main( sys.argv ) )

if __name__ == '__main__':
    main()
