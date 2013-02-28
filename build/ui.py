import os.path
import glob

from PyQt4 import uic

generated_ui_output = './..'

def process_ui_files():
    ui_files = (glob.glob('../ui/*.ui'))
    for f in ui_files:
        out_filename = (
            os.path.join(
                generated_ui_output,
                os.path.splitext(
                    os.path.basename(f))[0].replace(' ', '')+'.py')
        )
        out_file = open(out_filename, 'w')
        uic.compileUi(f, out_file)
        out_file.close()

if __name__ == '__main__':
    process_ui_files()