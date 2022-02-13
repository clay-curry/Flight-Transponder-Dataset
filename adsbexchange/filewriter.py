import json
import os
import zlib
import multiprocessing
import airspace as airspace

output_dir = str(os.path.dirname(f"{__file__}")) + "/adsb_raw"
# Lets get the output location


class FileWriter:
    def __init__(self, region) -> None:
        existing_files = os.listdir(output_dir)


if __name__ == "__main__":
    fw = FileWriter()
