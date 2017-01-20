from setuptools import setup

setup(name='user_sync',
      version='0.7.0',
      packages=['user_sync', 'user_sync.connector'],
      install_requires=[
          'pycrypto',
          'python-ldap==2.4.25',
          'PyYAML',
          'umapi-client',
          'psutil',
      ],
      entry_points={
          'console_scripts': [
              'user_sync = user_sync.app:main'
          ]
      },
)
