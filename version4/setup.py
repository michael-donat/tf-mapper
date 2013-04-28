from setuptools import setup

APP = ['main.py']
OPTIONS = {'argv_emulation': True, 'includes': ['sip', 'PyQt4._qt']}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
