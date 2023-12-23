import pandas as pd
import numpy as np
from talib import ATR


def chandelier_exit(
    data: pd.DataFrame,
    atr_period: int,
    atr_multiplier: float,
    use_close_price_for_extremums: bool,
):
    # Calculate ATR
    data["high"] = data["high"].astype("float64")
    data["low"] = data["low"].astype("float64")
    data["close"] = data["close"].astype("float64")
    atr_values = ATR(
        data["high"].values,
        data["low"].values,
        data["close"].values,
        timeperiod=atr_period,
    )
    atr_values = atr_values * atr_multiplier

    result_df = pd.DataFrame()
    result_df["ATR"] = atr_values

    # Initialize longStop and shortStop columns
    result_df["longStop"] = np.nan
    result_df["shortStop"] = np.nan

    # Calculate long and short stops
    for i in range(atr_period, len(data)):
        if use_close_price_for_extremums:
            highest_high = data["close"].iloc[i - atr_period : i].max()
            lowest_low = data["close"].iloc[i - atr_period : i].min()
        else:
            highest_high = data["high"].iloc[i - atr_period : i].max()
            lowest_low = data["low"].iloc[i - atr_period : i].min()

        if (
            np.isnan(result_df.loc[i - 1, "longStop"])
            or data.loc[i - 1, "close"] > result_df.loc[i - 1, "longStop"]
        ):
            result_df.loc[i, "longStop"] = max(
                highest_high - result_df.loc[i, "ATR"], result_df.loc[i - 1, "longStop"]
            )
        else:
            result_df.loc[i, "longStop"] = highest_high - result_df.loc[i, "ATR"]

        if (
            np.isnan(result_df.loc[i - 1, "shortStop"])
            or data.loc[i - 1, "close"] < result_df.loc[i - 1, "shortStop"]
        ):
            result_df.loc[i, "shortStop"] = min(
                lowest_low + result_df.loc[i, "ATR"], result_df.loc[i - 1, "shortStop"]
            )
        else:
            result_df.loc[i, "shortStop"] = lowest_low + result_df.loc[i, "ATR"]

    # Determine direction
    result_df["dir"] = np.where(
        data["close"] > result_df["shortStop"].shift(1),
        1,
        np.where(data["close"] < result_df["longStop"].shift(1), -1, np.nan),
    )
    result_df["dir"].ffill(inplace=True)

    # Determine buy and sell signals
    result_df["ca_buySignal"] = (result_df["dir"] == 1) & (
        result_df["dir"].shift(1) == -1
    )
    result_df["ca_sellSignal"] = (result_df["dir"] == -1) & (
        result_df["dir"].shift(1) == 1
    )

    return result_df
