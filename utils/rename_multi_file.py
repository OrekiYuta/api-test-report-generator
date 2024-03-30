import os
from utils.PathManager import load_path_manager as lpm

folder_input_jaeger = str(lpm.input("Jaeger-Screenshot"))
directory_path = folder_input_jaeger

for folder in os.listdir(directory_path):

    for filename in os.listdir(directory_path + "/" + folder):
        if "_" in filename:

            parts = filename.split("_")
            new_filename = parts[1] + ".png"

            new_filepath = os.path.join(directory_path + "/" + folder + "/" + new_filename)
            old_filepath = os.path.join(directory_path + "/" + folder + "/" + filename)
            os.rename(old_filepath, new_filepath)

        else:
            pass
