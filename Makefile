all: osx package upload

osx: build-osx package-osx upload-osx

build-osx:
	python2.7 make/osx-setup.py py2app  --dist-dir=dist/osx -bbuild/osx

win-pre:
	cp -r ./* /Volumes/C/tf-mapper-build/

win-post:
	mkdir -p dist/win
	zip -r dist/win/MudMapper.zip /Volumes/C/tf-mapper-build/dist/win/MudMapper

package-osx:
	mkdir -p dist/osx/dmg
	'cp' -rf dist/osx/MudMapper.app dist/osx/dmg/
	ln -s /Applications dist/osx/dmg/Applications
	hdiutil create dist/osx/MudMapper.dmg -srcfolder dist/osx/dmg/ -ov
	mv dist/osx/MudMapper.dmg dist/

package-win:
	mv dist/win/MudMapper.zip dist/

upload-osx:
	scp dist/MudMapper.dmg thornag@mahakam.pl:/home/thornag/public_html

upload-win:
	scp dist/MudMapper.zip thornag@mahakam.pl:/home/thornag/public_html
