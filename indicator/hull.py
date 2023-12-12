import pandas as pd
import numpy as np


# Define the functions
def weighted_moving_average(data, length):
    weights = np.arange(1, length + 1)
    return data.rolling(length).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def HMA(data, length):
    sqrt_length = int(np.sqrt(length))
    wma_half = weighted_moving_average(data, length // 2)
    wma_length = weighted_moving_average(data, length)
    raw_hma = 2 * wma_half - wma_length
    return weighted_moving_average(raw_hma, sqrt_length)


def calculate_hull(df, length):
    # Calculate the Hull Moving Average
    hull_df = pd.DataFrame()
    hull_df['hma'] = HMA(df['close'], length)
    # Determine the trend
    hull_df['longTrend'] = hull_df['hma'] > hull_df['hma'].shift(2)
    hull_df['shortTrend'] = ~hull_df['longTrend']
    return hull_df
