"""
Module containing callback definitions to be used in dashboard.
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import pytorch_forecasting as ptf
import wandb

from dash.dependencies import Input, Output, State
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.data.timeseries import TimeSeriesDataSet
from pytorch_forecasting.metrics import QuantileLoss
from wandb.sdk.wandb_config import Config

from app import app, cache
from utils.asset_loader import data_loader, model_loader
from utils.plotting import plot_country_prediction

from typing import Union, Any, List

def assign_callbacks(app: dash.Dash) -> None:
    """
    Load needed data into cache and assign callbacks to application
    """
    # URL to download data from
    URL: str = "https://covid.ourworldindata.org/data/owid-covid-data.json"

    # config file to read for model parameters
    # IDEA: add entry for model name in yml to make sure models can only bbe used with the
    # right config file
    CONF: str = "run_config.yml"
    run = wandb.init(mode="disabled", config=CONF)
    config: Config = run.config


    # load most recent data into cache to be used across callbacks
    # see https://dash.plotly.com/sharing-data-between-callbacks
    # as to why this is necessary
    @cache.cached(timeout=600)
    def prediction_timeseries() -> List[Any]:
        """
        Load most recent dataset to use in predictions and construct Timeseries
        object to run preedictions on.
        """

        # load data from URL
        data = data_loader.load_asset_from_url(URL)


        # get observations with insufficient data points

        indices_to_drop = data.groupby("location").agg("size").loc[
           (data.groupby("location").agg("size") <
            config.max_encoder_length)
           |
           (data.groupby("location").agg("size") <
            config.max_pred_length)
        ].index.to_list()

        #set training cutoff programatically
        config.training_cutoff = data['time_idx'].max() - config.max_pred_length

        # adjust data to match training format
        data.drop(index=data.loc[data.location.isin(indices_to_drop)].index, inplace=True)
        data = data.sort_values('location')

        # make new columns indicating what will be imputed
        cols_with_missing = (col for col in [
            *config.static_reals,
            *config.time_varying_known_reals,
            config.targets
        ] if data[col].isnull().any())

        for col in cols_with_missing:
            data[col + '_was_missing'] = data[col].isnull()

        data[[
            *config.static_reals,
            *config.time_varying_known_reals,
            config.targets
        ]] = data[[
        *config.static_reals,
        *config.time_varying_known_reals,
        config.targets]].fillna(0)


        impute_dummies = [col for
                          col in data.columns if col.endswith("_was_missing")]

        data[impute_dummies] = data[impute_dummies].astype("str").astype("category")

        # if the dataset still contains missing values for the target, count them and drop them
        missing_targets = data.loc[data[config.targets].isna()][["location","date"]].copy(deep=True)
        data.drop(index=missing_targets.index, inplace=True)

        # from pytorch tutorial
        # select last 180 days
        encoder_data = data[
        lambda x: x.time_idx > x.time_idx.max() - config.max_encoder_length
        ]

        last_data = data[lambda x: x.time_idx == x.time_idx.max()]
        decoder_data = pd.concat(
            [
                last_data.assign(
                date=lambda x: x.date + pd.DateOffset(days=i))
                for i in range(1, config.max_pred_length + 1)
            ],
            ignore_index=True,
        )

        # add time index consistent with "data"
        decoder_data["time_idx"] = decoder_data["date"].dt.year * 356 + decoder_data["date"].dt.day
        decoder_data["time_idx"] += encoder_data["time_idx"].max() + 1 - decoder_data["time_idx"].min()

        # adjust additional time feature(s)
        decoder_data["month"] = decoder_data.date.dt.month.astype(str).astype("category")  # categories have be strings

        # combine encoder and decoder data
        new_prediction_data = pd.concat([encoder_data, decoder_data], ignore_index=True)

        # create time series object
        pred_ts = TimeSeriesDataSet(
            new_prediction_data,
            group_ids=["location"],
            time_idx="time_idx",
            static_categoricals=['location', 'continent', 'tests_units'],
            static_reals = config.static_reals,
            time_varying_known_categoricals=['month', *impute_dummies], #allow for missings to be flagged on country-level over time - needs to be assumed in forecasts
            time_varying_known_reals=config.time_varying_known_reals,
            target_normalizer=GroupNormalizer(groups=['location'], transformation=config.transformation),
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
            target= config.targets,
            max_encoder_length=config.max_encoder_length,
            max_prediction_length=config.max_pred_length,
            predict_mode=True,
            allow_missings=True,
        )

        return [new_prediction_data, pred_ts]

    # new_prediction_data, pred_ts = prediction_timeseries()

    @app.callback(
        Output("latest-training-date","children"),
        Input("training-data-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_latest_training_date(path):
        """
        Callback to update last available training date
        """
        df = data_loader.load_asset(path)

        date = df.date.max()
        return date

    @app.callback(
        Output("country-selector", "options"),
        Input("latest-training-date","children"),
        prevent_initial_call=True
    )
    def update_country_selection(date):
        """
        Callback to update country list with allowed country indices
        Strictly this won't depend on the las training date, due to the way
        we prepare the data, but we need an input to trigger population of the index
        """
        if date:
            # get full prediction data (as df)
            pred_df, pred_ts = prediction_timeseries()

            # mapping of ISO3 names to country names
            iso_name_df = pd.read_csv("iso3.csv")
            iso_name_dict = dict(zip(iso_name_df.ISO3, iso_name_df.name))

            # build new index to account for dropped observations
            new_index = dict(
                tuple(
                    zip(
                       pred_df.location.unique(),
                       range(0,pred_df.location.nunique())
                    )
                )
            )

            # associate full names with index values of preedictions
            options = [
                {"label": iso_name_dict[location], "value": index}
                if (not location.startswith("OWID")) else
                {"label": location, "value": index}
                for location, index in new_index.items()
            ]

            return options
        else:
            return None

    @app.callback(
        Output("plotting-area", "children"),
        Input("country-selector", "value"),
        State("model-dropdown", "value"),
        State("latest-training-date","children"),
        prevent_initial_call=True
    )
    def plot_prediction(country_index, model_path, train_end):
        """
        Callback to load model and load prediction for country
        """

        # load specified model
        model = model_loader.load_asset(model_path)

        # get full prediction data (as df)
        pred_df, pred_ts = prediction_timeseries()

        day_zero = pred_df.date.max()

        # mapping of ISO3 names to country names
        iso_name_df = pd.read_csv("iso3.csv")
        iso_name_dict = dict(zip(iso_name_df.ISO3, iso_name_df.name))

        # build new index to map index -> iso
        new_index = dict(
            tuple(
                zip(
                   range(0,pred_df.location.nunique()),
                   pred_df.location.unique()
               )
            )
        )


        # get country name for plot title --> take care of OWID aggregates
        country_name = (
            new_index[country_index]
            if new_index[country_index].startswith("OWID") else
            iso_name_dict[new_index[country_index]]
        )

        # make predictions on TimeSeries object
        predictions, new_x = model.predict(pred_ts, mode="raw", return_x=True)

        # prepare data needed for plot
        figure = plot_country_prediction(model, predictions, new_x, country_index, country_name,
                                    day_zero, train_end)

        return dcc.Graph(
            figure=figure,
            )

    # end wandb run
    run.finish()
