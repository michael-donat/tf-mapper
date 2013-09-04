all: osx package upload

osx:
	python2.7 make/osx-setup.py py2app  --dist-dir=dist/osx -bbuild/osx

win-pre:
	cp -r ./* /Volumes/C/tf-mapper-build/

win-post:
	mkdir -p dist/win
	zip -r dist/win/MudMapper.zip /Volumes/C/tf-mapper-build/dist/win/MudMapper

package:
	hdiutil create dist/osx/MudMapper.dmg -srcfolder dist/osx/MudMapper.app -ov
	mv dist/osx/MudMapper.dmg dist/
	mv dist/win/MudMapper.zip dist/

upload:
	scp dist/MudMapper.dmg thornag@mahakam.pl:/home/thornag/public_html
	scp dist/MudMapper.zip thornag@mahakam.pl:/home/thornag/public_html
