# -*- coding: utf-8 -*-
"""
This strategy follows the following rules:
0. rb recommended bid
1. If your average rank is below 2, use rb to increase exposure.
2. If your average rank is above 2, use 0.9*min(rb, your_bid)

Ref: https://www.mobile01.com/topicdetail.php?f=747&t=6374199
"""
import pandas as pd
import numpy as np
import logging

def get_bid_of_item_func(item_dict, keyword=None):
    convert_percent = lambda x: float(x.rstrip('%').strip('+').replace(',','')) / 100.0 if isinstance(x, str) and x.endswith('%') else x
    convert_hyphen = lambda x: np.nan if isinstance(x, str) and x.endswith('-') else x
    # Apply the lambda function to all cells in the DataFrame
    df = item_dict.applymap(convert_percent)
    df = df.applymap(convert_hyphen)
    df = df.applymap(convert_to_float)
    yesterday_CTR = df['ClickThroughRate'][1]
    recommended_bid = min(df.RecommendedBid)
    your_current_bid = df.YourBid[0]
    current_rank = get_latest_value_in_col(df.AveragedRank)

    if yesterday_CTR < 0.05:
        logging.warning(f'Watch out: CTR of {keyword} is {yesterday_CTR} < 5%')

    if current_rank > 2.1:
        return {"strategy": round(recommended_bid, 2), "System Recommend": df.RecommendedBid[0], "CTR": yesterday_CTR}
    else:
        return {"strategy": round(0.9*min(recommended_bid, your_current_bid), 2), "System Recommend": df.RecommendedBid[0], "CTR": yesterday_CTR}


def get_latest_value_in_col(series: pd.Series) -> float:
    for i in series.dropna():
        if i!=np.nan:
            return i
    return None

def convert_to_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return np.nan
