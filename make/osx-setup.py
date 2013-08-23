from setuptools import setup

NAME = 'MudMapper'
VERSION = '1.7.8'
ID = 'tf-mapper'
COPYRIGHT = 'Copyright Michael Donat'
DATA_FILES = ['ui', 'make/qt.conf']

"""qt.conf as an empty file is needed cause of some bug, it will crash without it"""

plist = dict(
    CFBundleName                = NAME,
    CFBundleShortVersionString  = ' '.join([NAME, VERSION]),
    CFBundleVersion             = VERSION,
    CFBundleGetInfoString       = NAME,
    CFBundleExecutable          = NAME,
    CFBundleIdentifier          = 'net.michaeldonat.app.%s' % ID,
    NSHumanReadableCopyright    = COPYRIGHT
)


APP = [dict(script='main.py', plist=plist)]
OPTIONS = {'argv_emulation': True,
           'includes': ['sip', 'PyQt4._qt'],
           'iconfile':'ui/icons/hychsohn_256x256x32_transparent.icns',
           'frameworks': 'make/libQtCLucene.4.dylib'}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    data_files = DATA_FILES
)
