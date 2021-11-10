import datetime
import os
import pandas as pd
from typing import Union
import numpy as np
import yfinance as yf
from makeprediction.quasigp import QuasiGPR as qgpr
TODAY = datetime.date.today()

def train(ticker="MSFT"):
    # data = yf.download("^GSPC", "2008-01-01", TODAY.strftime("%Y-%m-%d"))
    data = yf.download(ticker, "2020-01-01", TODAY.strftime("%Y-%m-%d"))
    data.head()
    data["Adj Close"].plot(title=f"{ticker} Stock Adjusted Closing Price")

    df_forecast = data.copy()
    df_forecast.reset_index(inplace=True)
    df_forecast["ds"] = df_forecast["Date"]
    df_forecast.set_index("ds",inplace=True)

    df_forecast["y"] = df_forecast["Adj Close"]
    # df_forecast = df_forecast[["ds", "y"]]
    print('DATA', df_forecast.head())

    model = qgpr(df_forecast.index, df_forecast["Adj Close"].values)
    model.fit()
    model.save(f"{ticker}")

def predict(ticker="MSFT", horizon = '1d', freq = '1H'):
    now = datetime.datetime.now()

    model_file = f"{ticker}"
    if not os.path.isdir(model_file):
   #  if not model_file.exists():
        return False
    model = qgpr()
    model = model.load(model_file)
    freq = freq_to_seconds(freq)
    freq = f"{int(freq)}s"

    horizon = freq_to_seconds(horizon)
    future = now + datetime.timedelta(seconds=horizon)
    
    dates = pd.date_range(start=now, end=future.strftime("%m/%d/%Y %H:%M:%S"), freq = freq)
    y_pred, y_std = model.predict(dates,return_value = True)
    # if update_data == []:
    #     y_pred, y_std = model.predict(dates,return_value = True)
    # else:
    #     data = dict(x_update = update_data[0], y_update =  update_data[1])
    #     model.update(**data)
    #     # model.update(data)
    #     y_pred, y_std = model.predict(dates,return_value = True)

    forecast = pd.DataFrame( { 'y_pred': y_pred, 'y_std':y_std, 'date': dates.strftime("%m/%d/%Y %H:%M:%S")}   )
    return forecast.to_dict("records")

def update(ticker="MSFT", date = None, data = None):
    model_file = f"{ticker}"
    if not os.path.isdir(model_file):
   #  if not model_file.exists():
        return False
    model = qgpr()
    model = model.load(model_file)
    if date is None:
        return False
    date = pd.to_datetime(date)
    data = np.array(data)
    data = dict(x_update = date, y_update =  data)
    model.update(**data)
    return True


def convert(prediction_list):
    output = {}
    for data in prediction_list:
        date = data["date"]
        output[date] ={ 'Prediction': data["y_pred"],  'Upper bound 95%': data["y_pred"] + 1.96*data["y_std"], 'Lower bound 95%': data["y_pred"] - 1.96*data["y_std"]}
    return output




def freq_to_seconds(freq: Union[str, float]) -> float:
    """Transform a string that represents a duration or
       frequency into a duration in seconds.

    Extended description of function.

    Args:
        freq (str): a string duration like : '10s', '25m', '1.5h', '1d', '3w'

    Returns:
        float: duration in seconds

    """
    time_aliases = ['s', 'm', 'h', 'd', 'w']
    time_aliases_seconds = [1, 60, 60 * 60, 24 * 60 * 60, 7 * 24 * 60 * 60]
    if isinstance(freq, str):
        freq = freq.lower()
        freq = freq.replace(' ', '')
    # if freq in ['m','t','minute','minutes']:
    #     freq = 'm'
    for s in ['m','t','minute','minutes','min']:
        if freq.endswith(s):
            freq = freq.replace(s,'m')
    for s in ['d','day','days']:
        if freq.endswith(s):
            freq = freq.replace(s,'d')
    for s in ['s','sec','second','seconds']:
        if freq.endswith(s):
            freq = freq.replace(s,'s')
    for s in ['w','week','weeks']:
        if freq.endswith(s):
            freq = freq.replace(s,'w')
    for s in ['h','hour','hours']:
        if freq.endswith(s):
            freq = freq.replace(s,'h')

    if isinstance(freq, str) and any((freq.endswith(s) for s in time_aliases)):
        loc = np.argmax([freq.endswith(x) for x in time_aliases])
        string = time_aliases[loc]
        val = time_aliases_seconds[loc]

        try:
            if freq == string:
                v = 1
            else:
                v = float(freq.replace(string, ''))
            freq = v * val
            # print(f'{v} minutes')
        except (ValueError, TypeError) as err:
            msg = f"invalid custom frequency string: {freq}"
            raise ValueError(msg) from err
        return freq
    elif isinstance(freq, (int, float)):
        return freq
    else:
        msg = f"invalid value frequency: {freq}"
        raise ValueError(msg)

