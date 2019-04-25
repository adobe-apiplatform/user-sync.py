import os
import shutil


def cd():
    os.chdir(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))


def bundle_example_config():
    examples_dir = os.path.join('examples', 'config files - basic')
    files = [os.path.join(examples_dir, f) for f in os.listdir(examples_dir) if
             os.path.isfile(os.path.join(examples_dir, f))]
    bundle_dir = os.path.join('user_sync', 'resources', 'examples')
    if not os.path.exists(bundle_dir):
        os.mkdir(bundle_dir)
    for f in files:
        dest = os.path.join(bundle_dir, os.path.split(f)[-1])
        shutil.copy(f, dest)


if __name__ == '__main__':
    cd()
    bundle_example_config()
