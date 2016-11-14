from setuptools import setup

setup(name='aedash_user_sync',
      version='0.6.0',
      packages=['aedash', 'aedash.sync', 'aedash.sync.connector'],
      install_requires=[
          'pycrypto',
          'python-ldap==2.4.25',
          'PyYAML',
          'umapi',
          'psutil',
      ],
      entry_points={
          'console_scripts': [
              'aed_sync = aedash.sync.app:main'
          ]
      },
)
