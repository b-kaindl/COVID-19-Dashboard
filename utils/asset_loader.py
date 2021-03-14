from abc import ABC, abstractmethod
import data_retrieval
import os
import pandas as pd
from pytorch_forecasting import TemporalFusionTransformer
from typing import List, Dict, Any



class BaseLoader(ABC):
    """
    Base class for loading assets from a location.
    """

    def __init__(self, load_location: str, asset_type_ending: str=""):
        self.__load_location = load_location
        self.__asset_type_ending = asset_type_ending
        self.__file_list : List[str] = [
            entry for entry in os.listdir(self.__load_location)
            if entry.endswith(self.__asset_type_ending)
        ]

    @abstractmethod
    def load_asset(self, path: str) -> Any:
        """ Method to load an asset from the loader's file list"""
        pass


    def get_dropdown_entries(self) -> List[Dict[str,str]]:
        """
        List of Dictionaries to be passed to Dash Dropdown Menu
        """
        entries: List[Dict[str,str]] = []
        for file in self.__file_list:
            entry = {'label': file, 'value': self.__load_location + "/" +
                    file
                }
            entries.append(entry)
        return entries



class DataLoader(BaseLoader):
    """
    Class for loading Datasets from OWID
    """
    def __init__(self, load_location: str, asset_type_ending: str="", url:str = ""):
        super().__init__(load_location, asset_type_ending)

    def load_asset(self, path: str) -> pd.DataFrame:
        """
        Load dataset coming from OWID Covid Data and return cleaned DataFrame
        """
        raw = pd.read_json(path, orient="index")
        data_asset, x, info = data_retrieval.prepare_data(raw)
        return data_asset

    def load_asset_from_url(self, url: str):
        """
        Load dataset coming from OWID Covid Data and return cleaned DataFrame
        """
        raw = data_retrieval.retrieve_data_from_url(url)
        data_asset, x, info = data_retrieval.prepare_data(raw)
        return data_asset

    # def get_dropdown_entries(self) -> List[Dict[str,str]]:
    #     entries = super().get_dropdown_entries()
    #     return entries


class ModelLoader(BaseLoader):
    """
    Class for loading TFT models from checkpoint files
    """
    def __init__(self, load_location: str, asset_type_ending: str):
        super().__init__(load_location, asset_type_ending)

    def load_asset(self, path: str) -> TemporalFusionTransformer:
        """
        Load model from checkpoint file
        """
        model = TemporalFusionTransformer.load_from_checkpoint(path)
        return model

    # def get_dropdown_entries(self) -> List[Dict[str,str]]:
    #     entries = super().get_dropdown_entries()
    #     return entries


# initialize loaders to be used in app
data_loader = DataLoader("data")
model_loader = ModelLoader("models", ".ckpt")
