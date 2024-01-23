# datafile.py

import pandas as pd
import os
import signal
from datetime import datetime
from email.utils import formatdate
import sys

def print_err(text, end="\n"):
    # ANSI escape code for red
    RED = "\033[91m"
    RESET = "\033[0m"  # Reset color
    print(RED + text + RESET, file=sys.stderr, end=end)

class DataHandler:

    def save_main_file(self, signum=None, frame=None):
        pass

    def add_record_time(self, data):
        data['record_time'] = formatdate(localtime=True, usegmt=True)
        
    def append_data(self, data):
        pass

    def is_duplicate(self, current_data_key, second_key=None):
        pass

class DataFileHandler(DataHandler):
    def __init__(self, main_key, site, query):
        self.main_key = main_key
        self.site = site
        self.run_start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.main_csv_file = f'{self.site}-{query}.csv'
        self.temp_csv_file = f'{self.site}-{self.run_start_time}.csv'
        self.last_saved_main_key = self.__get_last_saved_key()
        print_err(f"last_saved_main_key={self.last_saved_main_key}")
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
        self.add_record_time(data)  # 添加时间戳
        df = pd.DataFrame([data])
        if not os.path.exists(self.temp_csv_file):
            df.to_csv(self.temp_csv_file, mode='w', index=False, header=True)
        else:
            df.to_csv(self.temp_csv_file, mode='a', index=False, header=False)

    def __get_last_saved_key(self):
        if os.path.exists(self.main_csv_file):
            df = pd.read_csv(self.main_csv_file)
            if not df.empty:
                return df.iloc[-1][self.main_key]
        return None

    def is_duplicate(self, current_data_key, second_key=None):
        #with CSV too expensive to find second key
        return current_data_key == self.last_saved_main_key


import sqlite3

class DataSQLiteHandler(DataHandler):
    def __init__(self, main_key, site, query, second_key=None):
        self.main_key = main_key
        self.second_key = second_key
        self.site = site
        self.query = query
        self.db_file = f'{self.site}_{self.query}.sqlite'
        self.table_name = f'{site}_{query}'
        self.__create_table()

    def __create_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        # 创建表时，确保也包括 second_key（如果有）
        table_columns = f"{self.main_key} TEXT PRIMARY KEY, record_time DATETIME"
        if self.second_key:
            table_columns += f", {self.second_key} TEXT"
        c.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} ({table_columns})')
        conn.commit()
        conn.close()

    def save_main_file(self, signum=None, frame=None):
        # 在SQLite中，此方法可能不需要，因为数据已经在数据库中
        pass

    def add_record_time(self, data):
        # 将时间格式化为 SQLite 接受的 datetime 格式
        data['record_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def append_data(self, data):
        self.add_record_time(data)
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # 检查并创建缺失的列
        c.execute(f'PRAGMA table_info({self.table_name});')
        existing_columns = {row[1] for row in c.fetchall()}
        for key in data.keys():
            if key not in existing_columns:
                c.execute(f'ALTER TABLE {self.table_name} ADD COLUMN {key} TEXT;')
                conn.commit()

        # 插入数据
        if self.second_key:
            # 确保 data 包含 second_key
            if self.second_key not in data:
                data[self.second_key] = ""  # 默认值统一为""

            columns = ', '.join(data.keys())
            placeholders = ':' + ', :'.join(data.keys())
            c.execute(f'INSERT OR REPLACE INTO {self.table_name} ({columns}) VALUES ({placeholders})', data)
        else:
            # 如果没有 second_key，使用普通的插入逻辑
            columns = ', '.join(data.keys())
            placeholders = ':'+', :'.join(data.keys())
            c.execute(f'INSERT OR IGNORE INTO {self.table_name} ({columns}) VALUES ({placeholders})', data)

        conn.commit()
        conn.close()

    def is_duplicate(self, current_data_key, current_second_key=None):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        if self.second_key and current_second_key is not None:
            # 如果 second_key 存在，且提供了 current_second_key，则检查两者
            c.execute(f'''SELECT COUNT(*) FROM {self.table_name}
                          WHERE {self.main_key} = ? AND {self.second_key} = ?''', 
                     (current_data_key, current_second_key))
        else:
            # 否则，只检查主键
            c.execute(f'SELECT COUNT(*) FROM {self.table_name} WHERE {self.main_key} = ?', (current_data_key,))

        result = c.fetchone()[0]
        conn.close()
        return result > 0
