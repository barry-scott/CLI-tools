import sys
import smart_find

def main():
    return smart_find.SmartFind( sys.argv ).execute()

if __name__ == '__main__':
    sys.exit( main() )
