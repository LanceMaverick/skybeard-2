from distutils.core import setup

config = {
    'description': 'A plugin based telegram bot',
    'author': 'LanceMaverick,',
    'url': 'https://github.com/LanceMaverick/skybeard-2/',
    'download_url': 'https://github.com/LanceMaverick/skybeard-2/releases/tag/2.1',
    'version': '2.1',
    'packages': ['skybeard'],
    'name': 'skybeard',
    'install_requires': [x.strip() for x in open("requirements.txt").readlines()],
    'entry_points': {
        'console_scripts': [
            'skybeard = skybeard.main:if__name____main__',
        ],
    }
}

setup(**config)
