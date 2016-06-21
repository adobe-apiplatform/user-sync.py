from setuptools import setup

setup(name='aedash_connector',
      version='0.5.0',
      packages=['aedash_connector'],
      install_requires=[
          'python-ldap',
          'PyYAML',
          'umapi',
      ],
      entry_points={
          'console_scripts': [
              'aedc = aedash_connector.app:main'
          ]
      },
)
