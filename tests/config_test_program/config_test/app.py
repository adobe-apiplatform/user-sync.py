import argparse
import yaml
from config_test.version import __version__ as APP_VERSION

def process_args():
    '''
    Validates the application arguments, and resolves the arguments into a Namespace object.
    :rtype: Namespace object with argument values mapped to destination properties. The mapping is defined in the
        argument parser.
    '''
    parser = argparse.ArgumentParser(description="User Sync Test from Adobe")
    parser.add_argument("-v", "--version",
                        action="version",
                        version="%(prog)s " + APP_VERSION)
    parser.add_argument("-f",
                        help="filename to load .",
                        metavar="filename",
                        dest="filename",
                        default=None)
    return parser.parse_args()


def main():
    args = process_args()

    if args.filename:
        filename = args.filename
    else:
        filename = "config.yml"

    with open(filename, 'rb', 1) as input_file:
        print input_file.read()

if __name__ == "__main__":
    main()
