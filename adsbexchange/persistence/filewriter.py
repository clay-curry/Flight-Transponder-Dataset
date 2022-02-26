import json
import os
import adsbexchange.datum.aircraft as aircraft
import zlib
import multiprocessing
import adsbexchange.datum.airspace as airspace


output_dir = str(os.path.dirname(f"{__file__}")) + "/track_data"


# Lets get the output location


class FileWriter:
    def __init__(self, region) -> None:
        existing_files = os.listdir(output_dir)
        file_indexes = [0].extend([int(word) for word in existing_files.split('_') if word.isdigit()])
        from datetime import datetime as dt
        now = dt.now()
        self.output_file = f'{max(file_indexes) + 1}_raw_adsb_{now}'
        

    

if __name__ == "__main__":
    fw = FileWriter()
