# datafile.py

import pandas as pd
import os
import signal
from datetime import datetime
from email.utils import formatdate

class DataFileHandler:
    def __init__(self, main_key, site, query):
        self.main_key = main_key
        self.site = site
        self.run_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.main_csv_file = f'{self.site}-{query}.csv'
        self.temp_csv_file = f'{self.site}-{self.run_start_time}.csv'
        self.last_saved_main_key = self.get_last_saved_key()
        print(f"last_saved_main_key={self.last_saved_main_key}")
        signal.signal(signal.SIGINT, self.save_main_file)

    def save_main_file(self, signum=None, frame=None):#signal handler(signum=None, frame=None)
        if os.path.exists(self.temp_csv_file):
            temp_df = pd.read_csv(self.temp_csv_file)
            if not temp_df.empty:
                reversed_df = temp_df.iloc[::-1]
                if os.path.exists(self.main_csv_file):
                    reversed_df.to_csv(self.main_csv_file, mode='a', index=False, header=False)
                else:
                    reversed_df.to_csv(self.main_csv_file, mode='w', index=False, header=True)
            os.remove(self.temp_csv_file)

    def append_data(self, data):
        data['record_time'] = formatdate(localtime=True, usegmt=True)
        df = pd.DataFrame([data])
        if not os.path.exists(self.temp_csv_file):
            df.to_csv(self.temp_csv_file, mode='w', index=False, header=True)
        else:
            df.to_csv(self.temp_csv_file, mode='a', index=False, header=False)

    def get_last_saved_key(self):
        if os.path.exists(self.main_csv_file):
            df = pd.read_csv(self.main_csv_file)
            if not df.empty:
                return df.iloc[-1][self.main_key]
        return None

    def is_duplicate(self, current_data_key):
        return current_data_key == self.last_saved_main_key

