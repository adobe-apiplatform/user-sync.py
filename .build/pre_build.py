import os
import shutil
from backports import configparser


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


def bundle_feature_flag_config():
    default_cfg_path = os.path.join('user_sync', 'resources', 'default_flags.cfg')
    default_cfg = configparser.ConfigParser()
    default_cfg.optionxform = str
    default_cfg.read(default_cfg_path)

    flag_data = {}

    for k, v in default_cfg.items('config'):
        env_val = os.environ.get(k)
        if env_val is not None:
            flag_data[k] = env_val
        else:
            flag_data[k] = v

    with open(os.path.join('user_sync', 'resources', 'flags.cfg'), 'w') as flag_cfg_file:
        flag_cfg = configparser.ConfigParser()
        flag_cfg.optionxform = str
        flag_cfg['config'] = flag_data
        flag_cfg.write(flag_cfg_file)


if __name__ == '__main__':
    cd()
    bundle_example_config()
    bundle_feature_flag_config()
