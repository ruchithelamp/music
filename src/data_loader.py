
import pandas as pd
import os

class DataLoader:
    def __init__(self, data_path):
        """ Initialize DataLaoader Object with a path to the data folder"""
        self.data_path = data_path

    def load_date(self, file_name):
        """ loads CSV from file_name
        params: file_name(str) : name of csv file to load
        returns: pd.Dataframe: loaded data as dataframe
        """

        fp = os.path.join(self.data_path, file_name)
        try:
            data = pd.read_csv(fp)
            print(f" Successfully loaded {file_name}")
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            return None
