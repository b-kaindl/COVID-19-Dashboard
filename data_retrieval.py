# TODO: split function into *testable* units
import numpy as np
import pandas as pd
import requests

from json.decoder import JSONDecodeError
from requests.exceptions import MissingSchema, ConnectionError

def retrieve_data_from_url(url):
    """
    Uses requests pkg to retrieve JSON data from URL and transform it into
    a pandas dataframe.

    Args:
        url (string): URL address to retrieve JSON from

    Returns:
        DataFrame: DataFrame containing JSON data

    Raises:
        Exception: Exceptions raised by imported pkgs

    """

    try:
        r = requests.get(url)
        data_json = r.json()
        data = pd.DataFrame.from_dict(data_json, "index")
    except (JSONDecodeError, MissingSchema, ConnectionError) as e:
        raise e

    return data

def prepare_data(df):
    """
    Prepares dataframe for analysis, and provides info on missing data

    Args:
        df (DataFrame): dataframe containing Covid data by OWID

    Returns:
        tuple: Tuple containing xs, ys, and info on data

    """

    # initialize dict containing further info
    info = {}

    # drop column containing explained variables and take out ys separately
    xs = df.drop(columns="data")
    raw_ys = df.data

    # get nans in xs
    x_nan_sums = xs.isnull().sum()
    x_nan_shares= xs.isnull().mean()

    # add info to dict as dicts
    info["x_nan_sums"] = dict(x_nan_sums)
    info["x_nan_shares"] = dict(x_nan_shares)
    info["x_shape"] = xs.shape

    # begin concatenating countries to get ys
    ys = pd.DataFrame(raw_ys[0])
    ys["location"] = raw_ys.index[0]
    ys = ys.set_index("location")
    ys = ys.reset_index()

    # append other countries
    for i in range(1,len(raw_ys)):
        new_ys = pd.DataFrame(raw_ys[i])
        new_ys["location"] = raw_ys.index[i]
        ys = ys.append(new_ys)

    # get nans in ys
    y_nan_sums = ys.isnull().sum()
    y_nan_shares= ys.isnull().mean()

    # add info to dict as dicts
    info["y_nan_sums"] = dict(y_nan_sums)
    info["y_nan_shares"] = dict(y_nan_shares)
    info["y_shape"] = ys.shape

    # join data sets to get complete df
    data = ys.join(xs, on='location',rsuffix="_x").drop(columns='location_x')

    # add info on size of complete df
    info["full_size"] = data.shape

    # prepare data for consumption by pytorch_forecasting
    data['date'] = pd.to_datetime(data['date'])
    t_zero = data['date'].min()
    data['time_idx'] = (data['date'] - t_zero).dt.days

    # fill world-level continent label
    data["continent"] = data["continent"].fillna('Global')

    # fill nans in test units
    data["tests_units"] = data["tests_units"].fillna('NA')

    # TODO: see if we might need additional features
    data["month"] = data.date.dt.month.astype(str).astype("category")
    data["continent"] = data["continent"].astype("category")
    data["tests_units"] = data["tests_units"].astype("category")

    # assign new unique index
    data.index = range(0,data.shape[0])

    return (data, xs, info)
