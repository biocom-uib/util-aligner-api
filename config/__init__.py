import os
import sys
import importlib


__all__ = ['config']


def get_config():
    settings_module = os.environ.get('APP_ENV')
    try:
        module = importlib.import_module(f'config.{settings_module}')
        settings = {k: v for k, v in vars(module).items()
                    if not k.startswith('_') and k.isupper()}
        return settings
    except Exception:
        sys.stderr.write('Failed to read config file: %s' % settings_module)
        sys.stderr.flush()
        raise


config = get_config()
