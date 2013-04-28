from distutils.core import setup
import py2exe

setup(name="MudMapper",
      version="1.0",
      author="Michael 'thornag' Donat",
      author_email="thornag@gmail.com",
      url="http://mapper.mahakam.pl",
      license="GNU General Public License (GPL)",
      options={"py2exe": {"skip_archive": True, "includes": ["sip", 'PyQt4._qt']}})