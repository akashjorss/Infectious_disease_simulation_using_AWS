from yapf.yapflib.yapf_api import FormatFile  # reformat a file
import os

rootdir = "./"
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(subdir, file)
            # print(filepath)
            FormatFile(file_path, in_place=True, style_config="pep8")
