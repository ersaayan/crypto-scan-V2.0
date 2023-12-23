import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
import talib


def calculate_rsi(df, column: str, n: int):
    return RSIIndicator(df[column], n).rsi()


def calculate_sma(df, column: str, n: int):
    return SMAIndicator(df[column], n).sma_indicator()


def calculate_ema(df, column: str, n: int):
    return EMAIndicator(df[column], n).ema_indicator()


def calculate_wma(df, column: str, n: int):
    return talib.WMA(df[column].values, timeperiod=n)


def calculate_bb(df, column: str, n: int, mult: float):
    indicator_bb = BollingerBands(df[column], window=n, window_dev=mult)
    new_df = pd.DataFrame()
    new_df["bb_bbm"] = indicator_bb.bollinger_mavg()
    new_df["bb_bbh"] = indicator_bb.bollinger_hband()
    new_df["bb_bbl"] = indicator_bb.bollinger_lband()
    return new_df


def crossover(series1, series2):
    return pd.Series((series1 > series2) & (series1.shift(1) < series2.shift(1)))


def crossunder(series1, series2):
    return pd.Series((series1 < series2) & (series1.shift(1) > series2.shift(1)))


def generate_signals(df, source_col, rsi_length, ma_type, ma_length, bb_std_dev):
    result_df = pd.DataFrame()
    result_df["rsi"] = calculate_rsi(df, source_col, rsi_length)

    if ma_type == "SMA":
        result_df["ma"] = calculate_sma(result_df, "rsi", ma_length)
    elif ma_type == "EMA":
        result_df["ma"] = calculate_ema(result_df, "rsi", ma_length)
    elif ma_type == "WMA":
        result_df["ma"] = calculate_wma(result_df, "rsi", ma_length)
    elif ma_type == "Bollinger Bands":
        result_df = calculate_bb(result_df, "rsi", ma_length, bb_std_dev)

    result_df["long_condition"] = crossover(result_df["rsi"], result_df["ma"])
    result_df["short_condition"] = crossunder(result_df["rsi"], result_df["ma"])

    return result_df
