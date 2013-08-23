from distutils.core import setup
import py2exe

NAME = 'MudMapper'
VERSION = '1.7.8'
ID = 'tf-mapper'
COPYRIGHT = 'Copyright Michael Donat'


setup(name=VERSION,
      version=VERSION,
      author="Michael 'thornag' Donat",
      author_email="thornag@gmail.com",
      url="http://mapper.mahakam.pl",
      license="GNU General Public License (GPL)",
      windows=[{"icon_resources": [(1, "ui/icons/hychsohn.ico")], "script" : "main.py"}],
      options={"py2exe" : {"dll_excludes": ["MSVCP90.dll"], "includes" : ["sip", "PyQt4"]}})
