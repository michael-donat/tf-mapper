osx:
	python2.7 build/osx-setup.py py2app  --dist-dir=dist/osx -bbuild/osx

package:
	hdiutil create dist/osx/MudMapper.dmg -srcfolder dist/osx/MudMapper.app -ov
	cd dist/win && zip -r MudMapper.zip MudMapper/ && cd -
	mv dist/osx/MudMapper.dmg dist/
	mv dist/win/MudMapper.zip dist/
	cd dist && mahcopy MudMapper.dmg && mahcopy MudMapper.zip && cd -
