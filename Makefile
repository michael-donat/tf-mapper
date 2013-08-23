all: osx package upload

osx:
	python2.7 make/osx-setup.py py2app  --dist-dir=dist/osx -bbuild/osx

package:
	hdiutil create dist/osx/MudMapper.dmg -srcfolder dist/osx/MudMapper.app -ov
	cd dist/win && zip -r MudMapper.zip MudMapper/ && cd -
	mv dist/osx/MudMapper.dmg dist/
	mv dist/win/MudMapper.zip dist/

upload:
	scp dist/MudMapper.dmg thornag@mahakam.pl:/home/thornag/public_html
	scp dist/MudMapper.zip thornag@mahakam.pl:/home/thornag/public_html
